from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from aphreco.pick import Picker
from aphreco.symbols import Symbols
from aphreco.types import ItemType

from . import rscargo, rsmain, rssampling, rssim, rsuse


class Writer:
    def __init__(self):
        self.rsparts: Dict[str, str] = OrderedDict(
            use=rsuse.APHRECO_PRELUDE,
            main="",
            const="",
            struct="",
            simtrait="",
            smp_t="",
            opttrait="",
            data="",
        )

    def write(self, picker: Picker, symbols: Symbols):
        # replace symbols in model equations
        repmap = self.create_repmap(symbols)
        source = self._replace_symbols(picker, repmap)

        # set rsparts
        self._write_sim_main()
        self._write_const(source)
        self._write_struct()
        self._write_sim_model(source)
        self._write_sampling_time()

        # connect rsparts
        rs_code = ""
        for str_part in self.rsparts.values():
            rs_code += str_part
        return rs_code

    def count_rsconst(self, picker: Picker):
        """count const number(LEN_Y, LNE_P, LEN_B) for the rust code"""
        len_y = picker.y.count("\n") + 1
        len_p = picker.p.count("\n") + 1
        len_b = picker.beat.count("\n") + 1
        return len_y, len_p, len_b

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

    def _replace_symbols(self, picker: Picker, repmap: Dict[str, str]):
        """replace symbols by y[i] or self.p[i]"""
        source = picker
        for name, code in repmap.items():
            source.ode = picker.ode.replace(name, code)
            source.rec = picker.rec.replace(name, code)
            source.beat = picker.beat.replace(name, code)
            source.cre = picker.cre.replace(name, code)

        return source

    def _write_sim_main(self):
        main_header = rsmain.HEADER
        main_body = rsmain.SIM_BODY
        main_footer = rsmain.FOOTER
        self.rsparts["main"] = main_header + main_body + main_footer

    def _write_const(self, source: Picker):
        len_y, len_p, len_b = self.count_rsconst(source)
        self.rsparts["const"] = rssim.write_const(len_y, len_p, len_b)

    def _write_struct(self):
        self.rsparts["struct"] = rssim.STRUCT

    def _write_sim_model(self, picker: Picker):
        # connect all
        model_code = rssim.IMPL_SIMTRAIT
        model_code += rssim.write_fn_new(picker.p)
        model_code += rssim.write_fn_init(picker.t, picker.y)
        model_code += rssim.write_fn_ode(picker.ode)
        model_code += rssim.write_fn_rec(picker.rec)
        model_code += rssim.write_fn_cond(picker.cond)
        model_code += rssim.write_fn_beat(picker.beat)
        model_code += rssim.write_fn_cre(picker.cre)
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.rsparts["simtrait"] = model_code

    def _write_sampling_time(self):
        self.rsparts["smp_t"] = rssampling.write_fn_sampling_time("")

    def _write_opt_model(self):
        pass

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
