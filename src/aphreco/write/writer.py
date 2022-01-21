from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from aphreco.pick import Picker
from aphreco.symbols import Symbols
from aphreco.types import ItemType, ProcType

from . import rscargo, rsmain, rsobs, rsopt, rssampling, rssim, rsuse


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

    def write(
        self,
        picker: Picker,
        symbols: Symbols,
        ptype: ProcType,
    ):
        # replace symbols in model equations
        repmap = self.create_repmap(symbols)
        replaced_picker = self._replace_symbols(picker, repmap)

        # set rsparts
        self._write_main(ptype)
        self._write_const(replaced_picker)
        self._write_struct()
        self._write_sim_model(replaced_picker)
        self._write_sampling_time()

        if ptype == ProcType.OPT:
            self._write_opt_model(replaced_picker)
            self._write_obs(replaced_picker)

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

    def _replace_symbols(self, picker: Picker, repmap: Dict[str, str]):
        """replace symbols by y[i] or self.p[i]"""
        replaced_picker = picker
        for name, code in repmap.items():
            replaced_picker.ode = picker.ode.replace(name, code)
            replaced_picker.rec = picker.rec.replace(name, code)
            replaced_picker.beat = picker.beat.replace(name, code)
            replaced_picker.cre = picker.cre.replace(name, code)

        return replaced_picker

    def _write_main(self, ptype: ProcType):
        main_header = rsmain.HEADER

        if ptype == ProcType.SIM:
            main_body = rsmain.SIM_BODY
        elif ptype == ProcType.OPT:
            main_body = rsmain.OPT_BODY

        main_footer = rsmain.FOOTER
        self.rsparts["main"] = main_header + main_body + main_footer

    def _write_const(self, reppicker: Picker):
        len_y, len_p, len_b = self.count_rsconst(reppicker)
        self.rsparts["const"] = rssim.write_const(len_y, len_p, len_b)

    def count_rsconst(self, reppicker: Picker):
        """count const number(LEN_Y, LNE_P, LEN_B) for the rust code"""
        len_y = reppicker.y.count("\n") + 1
        len_p = reppicker.p.count("\n") + 1
        len_b = reppicker.beat.count("\n") + 1
        return len_y, len_p, len_b

    def _write_struct(self):
        self.rsparts["struct"] = rssim.STRUCT

    def _write_sim_model(self, reppicker: Picker):
        # connect all
        model_code = rssim.IMPL_SIMTRAIT
        model_code += rssim.write_fn_new(reppicker.p)
        model_code += rssim.write_fn_init(reppicker.t, reppicker.y)
        model_code += rssim.write_fn_ode(reppicker.ode)
        model_code += rssim.write_fn_rec(reppicker.rec)
        model_code += rssim.write_fn_cond(reppicker.cond)
        model_code += rssim.write_fn_beat(reppicker.beat)
        model_code += rssim.write_fn_cre(reppicker.cre)
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.rsparts["simtrait"] = model_code

    def _write_sampling_time(self):
        self.rsparts["smp_t"] = rssampling.write_fn_sampling_time("")

    def _write_opt_model(self, reppicker: Picker):
        len_x = reppicker.y.count("\n") + 1
        str_opt_const = rsopt.write_const(len_x)
        self.rsparts["optconst"] = str_opt_const

        model_code = rsopt.IMPL_OPTTRAIT
        model_code += rsopt.write_fn_getx(reppicker.x_index, reppicker.x_bounds)
        model_code += rsopt.FN_GETP
        model_code += rsopt.FN_SETP
        model_code = model_code[:-1] + "}\n\n"  # end impl
        self.rsparts["opttrait"] = model_code

    def _write_obs(self, reppicker: Picker):
        self.rsparts["obs"] = rsobs.write_fn_obs(reppicker.obs)

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
