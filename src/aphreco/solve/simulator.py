from collections import OrderedDict

from aphreco.core import Model
from aphreco.enums import ItemType

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
    def __init__(self, stepper: BaseStepMethod = Dopri45()):
        if isinstance(stepper, BaseStepMethod):
            self.stepper = stepper
        else:
            raise TypeError("invalid stepper type")

        self.formatter = SimFormatter()
        # self.replacer = SimReplacer()
        # self.writer = SimWriter()
        # self.commander = SimCommander()

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
        terms_dict = model.collect_terms(OrderedDict())

        # unks_dicts = model.collect_unknowns(OrderedDict()) in Optimization

        # Format collected dicts into lines
        source = Source()
        source.lines["y"] = self.formatter.line_y(names_dict, vals_dict)
        source.lines["p"] = self.formatter.line_p(names_dict, vals_dict)

        print()
        print(source.lines["y"])
        print()
        print(source.lines["p"])

    def _execute(self):
        return SimResult(None)
