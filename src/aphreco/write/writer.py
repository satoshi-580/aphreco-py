from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from aphreco.symbols import Symbols
from aphreco.types import ItemType, ProcType

from .fn_main import rsmain
from .optimize import rsobs, rsopt
from .setup import rscargo, rsuse
from .simulate import rssampling, rssim
from .source import Source


class Writer:
    def __init__(self):
        self.rsparts: Dict[str, str] = OrderedDict(
            use=rsuse.APHRECO_PRELUDE,
            main="",
            const="",
            struct="",
            simtrait="",
            smp_t="",
            optconst="",
            opttrait="",
            obs="",
        )

    def reset(self):
        self.rsparts = OrderedDict(
            use=rsuse.APHRECO_PRELUDE,
            main="",
            const="",
            struct="",
            simtrait="",
            smp_t="",
            optconst="",
            opttrait="",
            obs="",
        )

    def write(
        self,
        source: Source,
        symbols: Symbols,
        ptype: ProcType,
    ):
        # delete previous strings in rsparts
        self.reset()

        # replace symbols in model equations
        repmap = self.create_repmap(symbols)
        replaced_source = self._replace_symbols(source, repmap)

        # set rsparts
        self._write_main(ptype)
        self._write_const(replaced_source)
        self._write_struct()
        self._write_sim_model(replaced_source)

        if ptype == ProcType.SIM:
            self._write_sampling_time()

        if ptype == ProcType.OPT:
            self._write_opt_model(replaced_source)
            self._write_obs(replaced_source)

        # connect rsparts
        rs_code = ""
        for str_part in self.rsparts.values():
            rs_code += str_part
        return rs_code

    def create_repmap(self, symbols: Symbols):
        """create a map for replacement
        symbol name: replaced string y[index] or p[index]
        """
        sorted_member = OrderedDict(
            sorted(symbols.member.items(), key=lambda k: len(k[0]), reverse=True)
        )

        repmap = OrderedDict()
        for name, (vtype, index) in sorted_member.items():
            if vtype == ItemType.Y:
                repmap[name] = "y[" + str(index) + "]"
            if vtype in (ItemType.P | ItemType.X):
                repmap[name] = "self.p[" + str(index) + "]"

        return repmap

    def _replace_symbols(self, source: Source, repmap: Dict[str, str]):
        """replace symbols by y[i] or self.p[i]"""
        replaced_source = source
        for name, code in repmap.items():
            replaced_source.ode = source.ode.replace(name, code)
            replaced_source.rec = source.rec.replace(name, code)
            replaced_source.beat = source.beat.replace(name, code)
            replaced_source.cre = source.cre.replace(name, code)

        return replaced_source

    def _write_main(self, ptype: ProcType):
        main_header = rsmain.HEADER

        if ptype == ProcType.SIM:
            main_body = rsmain.SIM_BODY
        elif ptype == ProcType.OPT:
            main_body = rsmain.OPT_BODY

        main_footer = rsmain.FOOTER
        self.rsparts["main"] = main_header + main_body + main_footer

    def _write_const(self, repsource: Source):
        len_y, len_p, len_b = self.count_rsconst(repsource)
        self.rsparts["const"] = rssim.write_const(len_y, len_p, len_b)

    def count_rsconst(self, repsource: Source):
        """count const number(LEN_Y, LNE_P, LEN_B) for the rust code"""
        len_y = repsource.y.count("\n") + 1
        len_p = repsource.p.count("\n") + 1
        len_b = repsource.beat.count("\n") + 1
        return len_y, len_p, len_b

    def _write_struct(self):
        self.rsparts["struct"] = rssim.STRUCT

    def _write_sim_model(self, repsource: Source):
        # connect all
        model_code = rssim.IMPL_SIMTRAIT
        model_code += rssim.write_fn_new(repsource.p)
        model_code += rssim.write_fn_init(repsource.t, repsource.y)
        model_code += rssim.write_fn_ode(repsource.ode)
        model_code += rssim.write_fn_rec(repsource.rec)
        model_code += rssim.write_fn_cond(repsource.cond)
        model_code += rssim.write_fn_beat(repsource.beat)
        model_code += rssim.write_fn_cre(repsource.cre)
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.rsparts["simtrait"] = model_code

    def _write_sampling_time(self):
        self.rsparts["smp_t"] = rssampling.write_fn_sampling_time("")

    def _write_opt_model(self, repsource: Source):
        len_x = repsource.x_index.count("\n") + 1
        str_opt_const = rsopt.write_const(len_x)
        self.rsparts["optconst"] = str_opt_const

        model_code = rsopt.IMPL_OPTTRAIT
        model_code += rsopt.write_fn_getx(repsource.x_index, repsource.x_bounds)
        model_code += rsopt.FN_GETP
        model_code += rsopt.FN_SETP
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.rsparts["opttrait"] = model_code

    def _write_obs(self, repsource: Source):
        self.rsparts["obs"] = rsobs.write_fn_obs(repsource.obs)

    def save(self, code: str, path: Optional[Path] = None):
        if path is None:
            path = Path.cwd()

        path_cargo_toml = path / "Cargo.toml"
        if not path_cargo_toml.exists():
            rscargo.create_toml(path_cargo_toml)

        # create src directory if not exists.
        path_src = path / "src"
        if not path_src.exists():
            path_src.mkdir()
        file_name = "main.rs"
        with open(path_src / file_name, "w") as f:
            f.write(code)

        path_res = path / "res"
        if not path_res.exists():
            path_res.mkdir()
        str_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = "aphrecode_" + str_now + ".rs"
        with open(path_res / file_name, "w") as f:
            f.write(code)

        return file_name
