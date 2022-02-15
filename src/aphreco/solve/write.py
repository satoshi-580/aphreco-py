import abc
from pathlib import Path
from typing import Dict

from .rust import rs_parts


class BaseWriter:
    def use_aphreco(self) -> str:
        return rs_parts.APHRECO_PRELUDE

    def start_main(self) -> str:
        return rs_parts.OPEN_MAIN

    def model_in_main(self) -> str:
        return rs_parts.LET_MODEL

    def close_main(self) -> str:
        return rs_parts.CLOSE_MAIN

    def struct(self) -> str:
        return rs_parts.STRUCT

    def open_simtrait(self) -> str:
        return rs_parts.OPEN_SIMTRAIT

    def close_simtrait(self) -> str:
        return rs_parts.CLOSE_SIMTRAIT

    @abc.abstractmethod
    def write_code(self, rep_lines: Dict[str, str], dirpath: Path) -> str:
        raise NotImplementedError


class SimWriter(BaseWriter):
    def __init__(self):
        pass

    def simulator_in_main(self, rep_lines: Dict[str, str]) -> str:
        method = rep_lines["stepper"]
        options = rep_lines["stepper_options"]
        codes_sim = rs_parts._let_stepper(method, options)
        codes_sim.append(rs_parts.LET_SIMULATOR)
        return "".join(codes_sim)

    def smptime_in_main(self) -> str:
        return rs_parts.LET_SMPTIME

    def runsim_in_main(self) -> str:
        return rs_parts.RUN_SIMULATOR

    def save_simres_in_main(self, dirpath: str) -> str:
        return rs_parts._save_simres(dirpath)

    def consts_ypb(self, rep_lines: Dict[str, str]) -> str:
        return "".join(
            [
                rs_parts._const_param_length("Y", rep_lines["y"]),
                rs_parts._const_param_length("P", rep_lines["p"]),
                rs_parts._const_param_length("B", rep_lines["beat"]),
            ]
        )

    def fn_new(self, p_lines: str) -> str:
        return rs_parts._fn_new(p_lines)

    def fn_init(self, t_lines: str, y_lines: str) -> str:
        return rs_parts._fn_init(t_lines, y_lines)

    def fn_ode(self, ode_lines: str) -> str:
        return rs_parts._fn_ode(ode_lines)

    def fn_rec(self, rec_lines: str) -> str:
        return rs_parts._fn_rec(rec_lines)

    def fn_cond(self, reg_cond_lines: str) -> str:
        return rs_parts._fn_cond(reg_cond_lines)

    def fn_beat(self, beat_lines: str) -> str:
        return rs_parts._fn_beat(beat_lines)

    def fn_cre(self, cre_lines: str) -> str:
        return rs_parts._fn_cre(cre_lines)

    def fn_smptime(self, smptime_lines: str) -> str:
        return rs_parts._fn_smptime(smptime_lines)

    def write_code(self, rep_lines: Dict[str, str], dirpath: Path) -> str:
        # import
        import_parts = [self.use_aphreco()]

        # main function
        main_parts = [
            "\n",
            self.start_main(),
            self.model_in_main(),
            self.simulator_in_main(rep_lines),
            self.smptime_in_main(),
            self.runsim_in_main(),
            self.save_simres_in_main(dirpath.name),
            self.close_main(),
        ]

        # model definition
        model_parts = [
            "\n",
            self.consts_ypb(rep_lines),
            self.struct(),
            self.open_simtrait(),
            self.fn_new(rep_lines["p"]),
            "\n",
            self.fn_init(rep_lines["t"], rep_lines["y"]),
            "\n",
            self.fn_ode(rep_lines["ode"]),
            "\n",
            self.fn_rec(rep_lines["rec"]),
            "\n",
            self.fn_cond(rep_lines["cond"]),
            "\n",
            self.fn_beat(rep_lines["beat"]),
            "\n",
            self.fn_cre(rep_lines["cre"]),
            self.close_simtrait(),
        ]

        # sampling time function
        smptime_parts = [self.fn_smptime(rep_lines["smptime"])]

        code_list = import_parts + main_parts + model_parts + smptime_parts
        return "".join(code_list)


class OptWriter(SimWriter):
    def data_in_main(self):
        return rs_parts.LET_DATA

    def obj_in_main(self):
        return rs_parts.LET_OBJECTIVE

    def optimizer_in_main(self, rep_lines: Dict[str, str]) -> str:
        method = rep_lines["optimizer"]
        options = rep_lines["optimizer_options"]
        code_opt = rs_parts._let_optimizer(method, options)
        return "".join(code_opt)

    def runopt_in_main(self):
        return rs_parts.RUN_OPTIMIZER

    def save_optres_in_main(self, dirpath: str) -> str:
        return rs_parts._save_optres(dirpath)

    def const_x(self, rep_lines: Dict[str, str]):
        return rs_parts._const_param_length("X", rep_lines["x_index"])

    def open_opttrait(self) -> str:
        return rs_parts.OPEN_OPTTRAIT

    def fn_getx(self, rep_lines):
        return rs_parts._fn_getx(rep_lines["x_index"], rep_lines["x_bounds"])

    def fn_getp(self):
        return rs_parts.FN_GETP

    def fn_setp(self):
        return rs_parts.FN_SETP

    def close_opttrait(self) -> str:
        return rs_parts.CLOSE_OPTTRAIT

    def fn_obs(self, data_lines):
        return rs_parts._fn_obs(data_lines)

    def write_code(self, rep_lines: Dict[str, str], dirpath: Path) -> str:
        # import
        import_parts = [self.use_aphreco()]

        # main function
        main_parts = [
            "\n",
            self.start_main(),
            self.model_in_main(),
            self.simulator_in_main(rep_lines),
            self.data_in_main(),
            self.obj_in_main(),
            "\n",
            self.optimizer_in_main(rep_lines),
            self.runopt_in_main(),
            self.save_optres_in_main(dirpath.name),
            self.close_main(),
        ]

        # model definition
        model_parts = [
            "\n",
            self.consts_ypb(rep_lines),
            self.struct(),
            # Simulator
            self.open_simtrait(),
            self.fn_new(rep_lines["p"]),
            "\n",
            self.fn_init(rep_lines["t"], rep_lines["y"]),
            "\n",
            self.fn_ode(rep_lines["ode"]),
            "\n",
            self.fn_rec(rep_lines["rec"]),
            "\n",
            self.fn_cond(rep_lines["cond"]),
            "\n",
            self.fn_beat(rep_lines["beat"]),
            "\n",
            self.fn_cre(rep_lines["cre"]),
            self.close_simtrait(),
            # Optimizer
            self.const_x(rep_lines),
            "\n",
            self.open_opttrait(),
            self.fn_getx(rep_lines),
            "\n",
            self.fn_getp(),
            "\n",
            self.fn_setp(),
            self.close_opttrait(),
        ]

        # observation function
        obs_parts = [self.fn_obs(rep_lines["obs"])]

        code_list = import_parts + main_parts + model_parts + obs_parts
        return "".join(code_list)


# class ExvWriter(OptWriter):
#     def run(self):
#         sects = super()._common_with_inherited()
#         list_import, list_main, list_const, list_model = sects
#         list_main.append(self._write_save_result())
#         list_main = rs_main.HEADER + list_main + rs_main.FOOTER
#         sections = list_import + list_main + list_const + list_model
#         return "".join(sections)

#     def _common_with_inherited(self):
#         sects = super()._common_with_inherited()
#         list_import, list_main, list_const, list_model = sects
#         list_main.append(self._write_excavator())
#         list_model.append(self._write_exv_trait())
#         return list_import, list_main, list_const, list_model

#     def _write_excavator(self):
#         return "let excavator = Excavator\n"

#     def _write_exv_trait(self):
#         return "impl ExvTrait for Model\n"

#     def _write_save_result(self):
#         return "exvres.save()"
