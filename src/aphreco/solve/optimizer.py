from collections import OrderedDict
from typing import Dict, Tuple

from aphreco.core import Model

from .fmin.base import BaseFminAlgorithm
from .fmin.serial import NelderMead
from .simulator import Simulator


class Optimizer(Simulator):
    def __init__(
        self,
        algo: BaseFminAlgorithm = NelderMead(),
        simulator: Simulator = Simulator(),
        **options,
    ):
        if not isinstance(algo, BaseFminAlgorithm):
            raise TypeError("invalid  type of algo")

        self.algo = algo
        if options:
            self.algo.set_options(**options)

        if not isinstance(simulator, Simulator):
            raise TypeError("invalid  type of simulator")

        self.simulator = simulator

    def run(
        self,
        model: Model,
        data,
        release=False,
    ):
        """generate a optimization code and run it immediately.

        Args:
            model (Model): The model object.

        Returns:
            OptResult: The simulated result

        """
        # dicts is a tuple of dictionaries (names_dict, vals_dict, terms_dict).
        dicts = self._collect_dicts(model)
        # lines = self._arrange_lines(dicts, smptime)
        # rep_lines = self._replace_names(lines, dicts[0])

    def _collect_dicts(self, model: Model) -> Tuple:
        names_dict, vals_dict, terms_dict = super()._collect_dicts(model)
        # unk_dict = model.collect_unknowns()
        unk_dict: Dict[str, float] = OrderedDict()
        return names_dict, vals_dict, terms_dict, unk_dict

    def _arrange_lines(
        self,
        dicts: Tuple,
        _=None,
    ) -> Dict[str, str]:
        # in BaseSolver._arrange_lines,
        # generate lines with y/p/ode/rec/cond/beat/cre/stepper/stepper_options.
        lines = super()._arrange_lines(dicts)

        # initial time of simulation
        vals_dict = dicts[1]
        if self.t0name not in vals_dict.keys():
            raise KeyError(f"Variable '{self.t0name}' is not in a model.")

        return lines
