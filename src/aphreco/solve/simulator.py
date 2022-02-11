from collections import OrderedDict
from decimal import Decimal
from typing import Dict, List, Tuple, Union

from aphreco.core import Model
from aphreco.enums import ItemType

from .format import SimFormatter
from .replace import SimReplacer
from .simulate.base import BaseStepMethod
from .simulate.dopri45 import Dopri45
from .write import SimWriter


def range_f2s(start: float, stop: float, step: float):
    dec_start = Decimal(str(start))
    dec_stop = Decimal(str(stop))
    dec_step = Decimal(str(step))

    for i in range(int((dec_stop - dec_start) / dec_step)):
        yield str(dec_start + i * dec_step)


class SimResult:
    def __init__(self, t):
        self.t = t
        self.y = None
        self.nfev = None


class Simulator:
    def __init__(
        self,
        stepper: BaseStepMethod = Dopri45(),
        starttime="starttime",
        **options,
    ):
        if not isinstance(stepper, BaseStepMethod):
            raise TypeError("invalid stepper type")

        self.starttime = starttime

        self.stepper = stepper
        if options:
            self.stepper.set_options(**options)

        self.formatter = SimFormatter()
        self.replacer = SimReplacer()
        self.writer = SimWriter()
        # self.commander = SimCommander()

    @property
    def simplify_eq(self):
        return self.formatter.simplify_eq

    @simplify_eq.setter
    def simplify_eq(self, simplify_eq):
        self.formatter.simplify_eq = simplify_eq

    def run(
        self,
        model: Model,
        smptime: Union[Tuple[float, float, float], List[float]],
    ):
        """generate a simulation code and run it immediately.

        Args:
            model (Model): The model object.
            smptime Union[Tuple[float, float, float], List[float]]: The output times of simulation.
                A tuple is interpreted as (start, stop, step).
                A list is interpreted as a vector of time points.

        Returns:
            SimResult: The simulated result

        """

        # dicts is a tuple of dictionaries (names_dict, vals_dict, terms_dict).
        dicts = self._collect_dicts(model)
        lines = self._arrange_lines(dicts, smptime)
        rep_lines = self._replace_names(lines, dicts[0])
        codes = self._write_codes(rep_lines)
        print()
        print(codes)

        simres = self._execute()
        return SimResult(smptime)

    def export(self, model: Model, smptime):
        print("just save a Rust code to run in another environment.")

    def _collect_dicts(self, model: Model) -> Tuple[Dict, Dict, Dict]:
        # Collect dicts from model items
        # names_dict: Dict[name(str), Tuple[itemtype(enums.ItemType), index(int)]]
        names_dict = model.set_yp_index(model.collect_names(OrderedDict()))

        # vals_dict : Dict[name(str), value(float)]
        vals_dict = model.collect_values(OrderedDict())

        # terms_dict: Dict[
        #     'ode': Dict[yname(str), rhs(str)],
        #     'rec': Dict[(start, stop, step), Dict[yname(str), rhs(str)]],
        #     'cre': Dict[yname(str), rhs(str)],
        # ]
        terms_dict = model.collect_terms(
            OrderedDict(
                ode=OrderedDict(),
                rec=OrderedDict(),
                cre=OrderedDict(),
            )
        )

        # ===== for debugging =====
        # print()  # debug terms_dict["ode"]
        # for lhs, rhs in terms_dict["ode"].items():
        #     print("deriv_" + lhs, "=", rhs)
        # print()  # debug terms_dict["rec"]
        # for beat, d in terms_dict["rec"].items():
        #     print("   ===", beat, "===")
        #     for lhs, rhs in d.items():
        #         print("delta_" + lhs, "+=", rhs)
        # print()  # debug terms_dict["cre"]
        # for lhs, rhs in terms_dict["cre"].items():
        #     print(lhs, "=", rhs)
        # =====================

        # unks_dicts = model.collect_unknowns(OrderedDict()) in Optimization
        return names_dict, vals_dict, terms_dict

    def _arrange_lines(
        self,
        dicts: Tuple[Dict, Dict, Dict],
        smptime: Union[Tuple[float, float, float], List[float]],
    ) -> Dict[str, str]:
        names_dict, vals_dict, terms_dict = dicts
        lines = OrderedDict()
        # Format collected dicts into lines
        lines["t"] = str(vals_dict[self.starttime])
        lines["y"] = self.formatter.line_y(names_dict, vals_dict)
        lines["p"] = self.formatter.line_p(names_dict, vals_dict)

        lines["ode"] = self.formatter.arrange_ode(terms_dict["ode"])
        str_rec, str_cond, str_beat = self.formatter.arrange_rec(terms_dict["rec"])
        lines["rec"] = str_rec
        lines["cond"] = str_cond
        lines["beat"] = str_beat
        lines["cre"] = self.formatter.arrange_cre(terms_dict["cre"])

        # stepper, stepper_options,
        stepper, stepper_options = self._arrange_stepper()
        lines["stepper"] = stepper
        lines["stepper_options"] = stepper_options

        # smptime (sampling time)
        lines["smptime"] = self._arrange_smptime(smptime)

        # ===== for debugging =====
        # print()
        # print(source.lines["t"])
        # print(source.lines["y"])
        # print(source.lines["p"])
        # print(source.lines["ode"])
        # print(source.lines["rec"])
        # print(source.lines["cond"])
        # print(source.lines["beat"])
        # print(source.lines["cre"])
        # print(source.lines["stepper"])
        # print(source.lines["stepper_options"])
        # =====================
        return lines

    def _arrange_stepper(self):
        """
        simulator: Simulator
            .options: Dict[str, value]
        """
        if self.stepper.is_default:
            stepper_options = "default"
        else:
            stepper_options = ""
            for key, value in self.stepper.options.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                stepper_options += key + ": " + str(value) + ",\n"
        return self.stepper.name, stepper_options

    def _arrange_smptime(self, smptime: Union[Tuple[float, float, float], List[float]]):
        if isinstance(smptime, tuple) and len(smptime) == 3:
            start = float(smptime[0])
            stop = float(smptime[1])
            step = float(smptime[2])
            smptime_list = range_f2s(start, stop, step)
        elif isinstance(smptime, list):
            smptime_list = [str(float(t)) for t in smptime]
        else:
            raise ValueError(
                f"'smptime' must be a tuple of three values (start, stop, step) or a list of values [t0, t1, t2, ...]"
            )

        return ", ".join(smptime_list)

    def _replace_names(
        self,
        lines: Dict[str, str],
        names_dict: Dict[str, Tuple[ItemType, int]],
    ):
        repmap = self.replacer.create_repmap(names_dict)
        rep_lines = self.replacer.replace_names_in_terms(lines, repmap)
        return rep_lines

    def _write_codes(self, rep_lines: Dict[str, str]) -> str:
        # import
        import_parts = self.writer.use_aphreco()

        # main function
        main_parts = list("\n")
        main_parts.extend(self.writer.start_main())
        main_parts.extend(self.writer.model_in_main())
        main_parts.extend(self.writer.simulator_in_main(rep_lines))
        main_parts.extend(self.writer.smptime_in_main())
        main_parts.extend(self.writer.run_simulator_in_main())
        main_parts.extend(self.writer.close_main())

        # model definition
        model_parts = list()
        model_parts.extend(self.writer.consts_ypb(rep_lines))
        model_parts.extend(self.writer.struct())
        model_parts.extend(self.writer.open_simtrait())
        model_parts.extend(self.writer.fn_new(rep_lines["p"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_init(rep_lines["t"], rep_lines["y"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_ode(rep_lines["ode"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_rec(rep_lines["rec"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_cond(rep_lines["cond"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_beat(rep_lines["beat"]))
        model_parts.append("\n")
        model_parts.extend(self.writer.fn_cre(rep_lines["cre"]))
        model_parts.extend(self.writer.close_simtrait())

        # sampling time function
        smptime_parts = self.writer.fn_smptime(rep_lines["smptime"])

        codes_list = import_parts + main_parts + model_parts + smptime_parts
        return "".join(codes_list)

    def _execute(self):
        return SimResult(None)
