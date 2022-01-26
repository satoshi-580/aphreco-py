"""Writer objects that recieve a ReplacedSource object and write a Rust code.
BaseWriter: an abstract Writer class
SimWriter: a Writer class that is used for creating a simulation code
OptWriter: a Writer class that is used for creating a optimization code
"""

import abc
from datetime import datetime
from pathlib import Path

from .general import rs_cargo, rs_const, rs_main, rs_struct, rs_use
from .optimize import rs_data, rs_opt
from .simulate import rs_sim, rs_smp
from .source import ReplacedSource


class BaseWriter(abc.ABC):
    """Writer objects recieve a ReplacedSource object, write a Rust code,
    and save the file 'main.rs' in ./src directory.
    Writer objects also create Cargo.toml in a current directory
    so that Cargo can compile the code by 'cargo run'.
    """

    @abc.abstractmethod
    def run(self, rep_source: ReplacedSource):
        NotImplementedError

    @abc.abstractmethod
    def _common_with_inherited(self, rep_source: ReplacedSource):
        NotImplementedError

    def _write_use(self):
        return rs_use.APHRECO_PRELUDE

    def _write_model(self):
        return rs_main.LET_MODEL

    def _write_struct(self):
        return rs_struct.STRUCT

    def save(self, code: str):
        path = Path.cwd()

        # create Cargo.toml
        path_cargo_toml = path / "Cargo.toml"
        if not path_cargo_toml.exists():
            rs_cargo.create_toml(path_cargo_toml)

        # create src directory
        path_src = path / "src"
        if not path_src.exists():
            path_src.mkdir()

        # create res directory
        path_res = path / "res"
        if not path_res.exists():
            path_res.mkdir()

        # save the source code as main.rs
        file_name = "main.rs"
        with open(path_src / file_name, "w") as f:
            f.write(code)

        # save a backup file in res
        str_now = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = "aphrecode_" + str_now + ".rs"
        with open(path_res / file_name, "w") as f:
            f.write(code)

        return file_name


class SimWriter(BaseWriter):
    def run(self, rep_source: ReplacedSource):
        sects = self._common_with_inherited(rep_source)
        list_import, list_main, list_const, list_model = sects
        list_main.append(rs_main.RUN_SIMULATOR)
        list_main.append(self._write_save_result())
        list_main = [rs_main.HEADER] + list_main + [rs_main.FOOTER]
        list_smp_time = [self._write_smp_time()]
        sections = list_import + list_main + list_const + list_model + list_smp_time
        code = "".join(sections)
        self.save(code)

    def _common_with_inherited(self, rep_source: ReplacedSource):
        list_import = [super()._write_use()]

        list_main = [super()._write_model()]
        list_main.extend(
            self._list_simulator(
                rep_source.lines["stepper"], rep_source.lines["stepper_options"]
            )
        )

        list_const = [
            rs_const._const_for_length("Y", rep_source.lines["y"]),
            rs_const._const_for_length("P", rep_source.lines["p"]),
            rs_const._const_for_length("B", rep_source.lines["beat"]),
        ]

        list_model = list()
        list_model.append(super()._write_struct())
        list_model.extend(self._list_sim_trait(rep_source))

        return list_import, list_main, list_const, list_model

    # common parts with OptWriter class
    def _list_simulator(self, stepper, stepper_options):
        list_sim = list()
        list_sim.append(rs_main._write_let_stepper(stepper, stepper_options))
        list_sim.append(rs_main.LET_SIMULATOR)
        return list_sim

    def _list_sim_trait(self, rep_source: ReplacedSource):
        sim_trait = [
            rs_sim.IMPL_SIMTRAIT,
            rs_sim.write_fn_new(rep_source.lines["p"]),
            rs_sim.write_fn_init(rep_source.lines["t"], rep_source.lines["y"]),
            rs_sim.write_fn_ode(rep_source.lines["ode"]),
            rs_sim.write_fn_rec(rep_source.lines["rec"]),
            rs_sim.write_fn_cond(rep_source.lines["cond"]),
            rs_sim.write_fn_beat(rep_source.lines["beat"]),
            rs_sim.write_fn_cre(rep_source.lines["cre"]),
            rs_sim.END_IMPL_SIMTRAIT,
        ]
        return sim_trait

    # unique: not used in OptWriter
    def _write_smp_time(self):
        return rs_smp.str_fn_sampling_time("")

    def _write_save_result(self):
        return """  simres.save("./res")"""


class OptWriter(SimWriter):
    def run(self, rep_source: ReplacedSource):
        sects = self._common_with_inherited(rep_source)
        list_import, list_main, list_const, list_model = sects
        list_main.append(rs_main.RUN_OPTIMIZER)
        list_main.append(self._write_save_result())
        list_main = [rs_main.HEADER] + list_main + [rs_main.FOOTER]
        list_obs = [self._write_fn_obs(rep_source)]
        sections = list_import + list_main + list_const + list_model + list_obs
        code = "".join(sections)
        self.save(code)

    def _common_with_inherited(self, rep_source: ReplacedSource):
        sects = super()._common_with_inherited(rep_source)
        list_import, list_main, list_const, list_model = sects

        list_main.extend([rs_main.LET_DATA, rs_main.LET_OBJECTIVE])
        list_main.extend(
            self._list_optimizer(
                rep_source.lines["optimizer"], rep_source.lines["optimizer_options"]
            )
        )

        list_const.append(rs_const._const_for_length("X", rep_source.lines["x_index"]))

        list_model.append(self._write_opt_trait(rep_source))

        return list_import, list_main, list_const, list_model

    # common parts with ExcWriter class
    def _list_optimizer(self, optimizer, optimizer_options):
        return rs_main._write_let_optimizer(optimizer, optimizer_options)

    def _write_opt_trait(self, rep_source: ReplacedSource):
        opt_trait = [
            rs_opt.IMPL_OPTTRAIT,
            rs_opt.write_fn_getx(
                rep_source.lines["x_index"], rep_source.lines["x_bounds"]
            ),
            rs_opt.FN_GETP,
            rs_opt.FN_SETP,
            rs_opt.END_IMPL_OPTTRAIT,
        ]
        return "".join(opt_trait)

    # unique
    def _write_save_result(self):
        return rs_main.SAVE_OPTRES

    def _write_fn_obs(self, rep_source: ReplacedSource):
        return rs_data.write_fn_obs(rep_source.lines["obs"])


class ExvWriter(OptWriter):
    def run(self):
        sects = super()._common_with_inherited()
        list_import, list_main, list_const, list_model = sects
        list_main.append(self._write_save_result())
        list_main = rs_main.HEADER + list_main + rs_main.FOOTER
        sections = list_import + list_main + list_const + list_model
        return "".join(sections)

    def _common_with_inherited(self):
        sects = super()._common_with_inherited()
        list_import, list_main, list_const, list_model = sects
        list_main.append(self._write_excavator())
        list_model.append(self._write_exv_trait())
        return list_import, list_main, list_const, list_model

    def _write_excavator(self):
        return "let excavator = Excavator\n"

    def _write_exv_trait(self):
        return "impl ExvTrait for Model\n"

    def _write_save_result(self):
        return "exvres.save()"
