import abc
from collections import OrderedDict
from typing import Dict, Tuple

from aphreco.core import Model
from aphreco.enums import ItemType


class BaseSolver(abc.ABC):
    @property
    def formatter(self):
        return self._formatter

    @formatter.setter
    def formatter(self, formatter):
        self._formatter = formatter

    @property
    def replacer(self):
        return self._replacer

    @replacer.setter
    def replacer(self, replacer):
        self._replacer = replacer

    @property
    def writer(self):
        return self._writer

    @writer.setter
    def writer(self, writer):
        self._writer = writer

    @property
    def exporter(self):
        return self._exporter

    @exporter.setter
    def exporter(self, exporter):
        self._exporter = exporter

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, command):
        self._command = command

    @property
    def reader(self):
        return self._reader

    @reader.setter
    def reader(self, reader):
        self._reader = reader

    def _collect_dicts(self, model: Model) -> Tuple:
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
        dicts: Tuple,
    ) -> Dict[str, str]:
        names_dict, vals_dict, terms_dict = dicts
        lines = OrderedDict()
        # Format collected dicts into lines
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

        # ===== for debugging =====
        # print()
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
        Returns:
            Tuple[str, str]
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

    def _replace_names(
        self,
        lines: Dict[str, str],
        names_dict: Dict[str, Tuple[ItemType, int]],
    ):
        repmap = self.replacer.create_repmap(names_dict)
        rep_lines = self.replacer.replace_names_in_terms(lines, repmap)
        return rep_lines

    def _export_codes(self, codes: str):
        self.exporter.create_main(codes)

    def _execute(self, release):
        if release:
            self.command.release()
        else:
            self.command.compile()

    def read(self, dirpath, ynames=None):
        return self.reader.read(dirpath, ynames)
