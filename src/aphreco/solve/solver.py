from collections import OrderedDict
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Tuple, Union

from aphreco.core import Model
from aphreco.enums import ItemType

from .command import Command
from .export import Exporter
from .format import SimFormatter
from .read import SimResReader
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


class Simulator:
    def __init__(
        self,
        stepper: BaseStepMethod = Dopri45(),
        t0name="t0",
        **options,
    ):
        if not isinstance(stepper, BaseStepMethod):
            raise TypeError("invalid stepper type")

        self.t0name = t0name

        self.stepper = stepper
        if options:
            self.stepper.set_options(**options)

        self.formatter = SimFormatter()
        self.replacer = SimReplacer()
        self.writer = SimWriter()
        self.exporter = Exporter()
        self.command = Command()
        self.reader = SimResReader()

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
        release=False,
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

        # make a directory for export
        # and the directory path is embedded to a rust code.
        self.exporter.setup_env()
        self.dirpath = self.exporter.mkdir_new_res()

        codes = self._write_codes(rep_lines, self.dirpath)
        self._export_codes(codes)
        self._execute(release)

        # read simulated results
        simres = self.read(self.dirpath, model.ynames)
        return simres

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
        if self.t0name not in vals_dict.keys():
            raise KeyError(f"Variable '{self.t0name}' is not in a model.")
        lines["t"] = str(vals_dict[self.t0name])
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
            try:
                smptime_list = [str(t) for t in smptime]
            except:
                raise ValueError

        return ", ".join(smptime_list)

    def _replace_names(
        self,
        lines: Dict[str, str],
        names_dict: Dict[str, Tuple[ItemType, int]],
    ):
        repmap = self.replacer.create_repmap(names_dict)
        rep_lines = self.replacer.replace_names_in_terms(lines, repmap)
        return rep_lines

    def _write_codes(self, rep_lines: Dict[str, str], dirpath: Path) -> str:
        # import
        import_parts = [self.writer.use_aphreco()]

        # main function
        main_parts = [
            "\n",
            self.writer.start_main(),
            self.writer.model_in_main(),
            self.writer.simulator_in_main(rep_lines),
            self.writer.smptime_in_main(),
            self.writer.runsim_in_main(),
            self.writer.save_simres_in_main(dirpath.name),
            self.writer.close_main(),
        ]

        # model definition
        model_parts = [
            "\n",
            self.writer.consts_ypb(rep_lines),
            self.writer.struct(),
            self.writer.open_simtrait(),
            self.writer.fn_new(rep_lines["p"]),
            "\n",
            self.writer.fn_init(rep_lines["t"], rep_lines["y"]),
            "\n",
            self.writer.fn_ode(rep_lines["ode"]),
            "\n",
            self.writer.fn_rec(rep_lines["rec"]),
            "\n",
            self.writer.fn_cond(rep_lines["cond"]),
            "\n",
            self.writer.fn_beat(rep_lines["beat"]),
            "\n",
            self.writer.fn_cre(rep_lines["cre"]),
            self.writer.close_simtrait(),
        ]

        # sampling time function
        smptime_parts = [self.writer.fn_smptime(rep_lines["smptime"])]

        codes_list = import_parts + main_parts + model_parts + smptime_parts
        return "".join(codes_list)

    def _export_codes(self, codes: str):
        self.exporter.create_main(codes)

    def _execute(self, release):
        if release:
            self.command.release()
        else:
            self.command.compile()

    def read(self, dirpath, ynames=None):
        return self.reader.read(dirpath, ynames)


class Optimizer:
    def __init__(self):
        pass
