from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

from . import rscargo, rsmain, rssampling, rssim, rsuse
from .picker import Picker


class Writer:
    def __init__(self):
        self.rsparts: Dict[str, str] = OrderedDict(
            use=rsuse.APHRECO_PRELUDE,
            main="",
            struct="",
            simtrait="",
            smp_t="",
            opttrait="",
            data="",
        )

    def write(self, source: Picker):
        #  set self.main
        self._write_sim_main()

        # set self.struct
        self._write_struct()

        # set self.simtrait
        self._write_sim_model(source)

        # set self.sampling_time
        self._write_sampling_time(source)

        rs_code = ""
        rs_code += self.rsparts["use"]
        rs_code += self.rsparts["main"]
        rs_code += self.rsparts["struct"]
        rs_code += self.rsparts["simtrait"]
        rs_code += self.rsparts["smp_t"]
        return rs_code

    def _write_sim_main(self):
        main_header = rsmain.HEADER
        main_body = rsmain.SIM_BODY
        main_footer = rsmain.FOOTER
        self.rsparts["main"] = main_header + main_body + main_footer

    def _write_struct(self):
        model_const = rssim.CONST
        struct = rssim.STRUCT
        self.rsparts["struct"] = model_const + struct

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

    def _write_sampling_time(self, picker: Picker):
        self.rsparts["smp_t"] = rssampling.write_fn_sampling_time("")

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

        str_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        # file_name = "aphrecode_" + str_now + ".rs"
        file_name = "main.rs"
        with open(path_src / file_name, "w") as f:
            f.write(code)

        return file_name
