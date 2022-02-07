from collections import OrderedDict

from aphreco.core import Model

from .format import SimFormatter
from .simulate.base import BaseStepMethod
from .simulate.dopri45 import Dopri45
from .source import Source


class SimResult:
    def __init__(self, t):
        self.t = t
        self.y = None
        self.nfev = None


class Simulator:
    def __init__(
        self,
        stepper: BaseStepMethod = Dopri45(),
        stepper_options=None,
        starttime="starttime",
    ):
        if isinstance(stepper, BaseStepMethod):
            self.stepper = stepper
        else:
            raise TypeError("invalid stepper type")

        self.starttime = starttime
        self.formatter = SimFormatter()
        # self.replacer = SimReplacer()
        # self.writer = SimWriter()
        # self.commander = SimCommander()

    @property
    def simplify_eq(self):
        return self.formatter.simplify_eq

    @simplify_eq.setter
    def simplify_eq(self, simplify_eq):
        self.formatter.simplify_eq = simplify_eq

    def run(self, model: Model, outtime):
        """generate a simulation code and run it immediately.

        Args:
            model (Model): The model object.
            outtime (List[float]): The output times of simulation.

        Returns:
            SimResult: The simulated result

        """

        self._prepare(model)
        simres = self._execute()
        return SimResult(outtime)

    def export(self, model: Model, outtime):
        print("just save a Rust code to run in another environment.")

    def _prepare(self, model: Model):
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

        # Format collected dicts into lines
        source = Source()

        source.lines["t"] = vals_dict[self.starttime]
        source.lines["y"] = self.formatter.line_y(names_dict, vals_dict)
        source.lines["p"] = self.formatter.line_p(names_dict, vals_dict)

        source.lines["ode"] = self.formatter.arrange_ode(terms_dict["ode"])
        str_rec, str_cond, str_beat = self.formatter.arrange_rec(terms_dict["rec"])
        source.lines["rec"] = str_rec
        source.lines["cond"] = str_cond
        source.lines["beat"] = str_beat
        source.lines["cre"] = self.formatter.arrange_cre(terms_dict["cre"])

        # stepper, stepper_options,
        stepper, stepper_options = self._arrange_stepper()
        source.lines["stepper"] = stepper
        source.lines["stepper_options"] = stepper_options

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

    def _execute(self):
        return SimResult(None)
