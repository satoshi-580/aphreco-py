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


class OptWriter(SimWriter):
    def data_in_main(self):
        return rs_parts.LET_DATA

    def obj_in_main(self):
        return rs_parts.LET_OBJECTIVE

    # def optimizer_in_main(self, rep_lines: Dict[str, str]) -> str:
    #     codes_opt = list()
    #     list_main.extend(
    #         self._list_optimizer(
    #             rep_source.lines["optimizer"], rep_source.lines["optimizer_options"]
    #         )
    #     )
    #     return "".join(codes_sim)


# class OptWriter(SimWriter):
#     def run(self, rep_source: ReplacedSource):
#         sects = self._common_with_inherited(rep_source)
#         list_import, list_main, list_const, list_model = sects
#         list_main.append(rs_main.RUN_OPTIMIZER)
#         list_main.append(self._write_save_result())
#         list_main = [rs_main.HEADER] + list_main + [rs_main.FOOTER]
#         list_obs = [self._write_fn_obs(rep_source)]
#         sections = list_import + list_main + list_const + list_model + list_obs
#         code = "".join(sections)
#         self.save(code)

#     def _common_with_inherited(self, rep_source: ReplacedSource):
#         sects = super()._common_with_inherited(rep_source)
#         list_import, list_main, list_const, list_model = sects

#         list_main.extend([rs_main.LET_DATA, rs_main.LET_OBJECTIVE])
#         list_main.extend(
#             self._list_optimizer(
#                 rep_source.lines["optimizer"], rep_source.lines["optimizer_options"]
#             )
#         )

#         list_const.append(rs_const._const_for_length("X", rep_source.lines["x_index"]))

#         list_model.append(self._write_opt_trait(rep_source))

#         return list_import, list_main, list_const, list_model

#     # common parts with ExcWriter class
#     def _list_optimizer(self, optimizer, optimizer_options):
#         return rs_main._write_let_optimizer(optimizer, optimizer_options)

#     def _write_opt_trait(self, rep_source: ReplacedSource):
#         opt_trait = [
#             rs_opt.IMPL_OPTTRAIT,
#             rs_opt.write_fn_getx(
#                 rep_source.lines["x_index"], rep_source.lines["x_bounds"]
#             ),
#             rs_opt.FN_GETP,
#             rs_opt.FN_SETP,
#             rs_opt.END_IMPL_OPTTRAIT,
#         ]
#         return "".join(opt_trait)

#     # unique
#     def _write_save_result(self):
#         return rs_main.SAVE_OPTRES

#     def _write_fn_obs(self, rep_source: ReplacedSource):
#         return rs_data.write_fn_obs(rep_source.lines["obs"])


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
