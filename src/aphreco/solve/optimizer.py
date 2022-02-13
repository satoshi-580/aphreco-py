from collections import OrderedDict
from typing import Dict, Optional, Tuple

from aphreco.core import Model

from .base import BaseSolver
from .format import OptFormatter
from .opt.base import BaseFminAlgorithm
from .opt.serial import NelderMead
from .simulator import Simulator


class Optimizer(BaseSolver):
    def __init__(
        self,
        algorithm: BaseFminAlgorithm = NelderMead(),
        simulator: Simulator = Simulator(),
        **options,
    ):
        if not isinstance(algorithm, BaseFminAlgorithm):
            raise TypeError("invalid  type of algo")

        self.algorithm = algorithm
        if options:
            self.algorithm.set_options(**options)

        if not isinstance(simulator, Simulator):
            raise TypeError("invalid  type of simulator")

        self.simulator = simulator
        self.formatter = OptFormatter()
        # self.replacer = SimReplacer()
        # self.writer = SimWriter()
        # self.exporter = Exporter()
        # self.command = Command()
        # self.reader = SimResReader()

    def run(
        self,
        model: Model,
        obs,
        now=True,
        release=False,
        simplify=False,
    ):
        """generate a optimization code and run it immediately.

        Args:
            model (Model): The model object.
            data (??): The observation data used in fmin.

        Returns:
            OptResult: The simulated result

        """
        # check args
        if simplify:
            self.formatter.simplify_eq = True

        # dicts is a tuple of dictionaries (names_dict, vals_dict, terms_dict).
        names_dict = model.set_yp_index(model.collect_names(OrderedDict()))
        vals_dict = model.collect_values(OrderedDict())
        terms_dict = model.collect_terms(
            OrderedDict(
                ode=OrderedDict(),
                rec=OrderedDict(),
                cre=OrderedDict(),
            )
        )
        unks_dict = model.set_x_index(model.collect_unknowns(OrderedDict()), names_dict)

        # ====================
        # format lines
        # generate lines with t/y/p/ode/rec/cond/beat/cre and /x_index/x_bounds.
        lines = self.formatter.format_model_info(
            (names_dict, vals_dict, terms_dict, unks_dict)
        )
        # lines of solver settings
        lines = self.formatter.format_simulator_info(lines, self.simulator)
        lines = self.formatter.format_optimizer_info(lines, self)
        # unique lines: in the case of simulation, add the following keys,
        #     lines["data"]: observation data
        lines = self.formatter.format_obs_info(lines, obs)

        for _, line in lines.items():
            print(line)

        # rep_lines = self._replace_names(lines, dicts[0])
