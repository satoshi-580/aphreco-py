from collections import OrderedDict

from aphreco.core import Data, Model

from .base import BaseSolver
from .command import Command
from .export import Exporter
from .fmin.base import BaseFminAlgorithm
from .fmin.serial import NelderMead
from .format import OptFormatter
from .read import OptResReader
from .replace import Replacer
from .simulator import Simulator
from .write import OptWriter


class Optimizer(BaseSolver):
    def __init__(
        self,
        method: BaseFminAlgorithm = NelderMead(),
        simulator: Simulator = Simulator(),
        **options,
    ):
        if not isinstance(method, BaseFminAlgorithm):
            raise TypeError("invalid  type of algo")

        self.method = method
        if options:
            self.method.set_options(**options)

        if not isinstance(simulator, Simulator):
            raise TypeError("invalid  type of simulator")

        self.simulator = simulator
        self.formatter = OptFormatter()
        self.replacer = Replacer()
        self.exporter = Exporter()
        self.writer = OptWriter()
        self.command = Command()
        self.reader = OptResReader()

    def run(
        self,
        model: Model,
        data: Data,
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

        # collect the following dictionaries from a model
        #     names_dict: y/p names
        #     vals_dict : y/p values
        #     terms_dict: terms in con/reg edges
        #     unks_dict : x names, p_index, bounds
        names_dict = model.set_yp_index(model.collect_names(OrderedDict()))
        vals_dict = model.collect_values(OrderedDict())
        vals_dict = model.collect_var_indices(vals_dict, names_dict)
        terms_dicts = model.collect_terms((OrderedDict(), OrderedDict(), OrderedDict()))
        unks_dict = model.set_x_index(model.collect_unknowns(OrderedDict()), names_dict)

        # ====================
        # format lines
        # generate lines with t/y/p/ode/rec/cond/beat/cre and /x_index/x_bounds,
        # and lines of solver settings.
        lines = self.formatter.format_model_info(
            (names_dict, vals_dict, terms_dicts, unks_dict)
        )
        lines = self.formatter.format_simulator_info(lines, self.simulator)
        lines = self.formatter.format_optimizer_info(lines, self)
        # unique lines: in the case of simulation, add the following keys,
        #     lines["obs"]: observation data
        data.set_yindex(names_dict)
        data.sort_by_index()
        lines = self.formatter.format_obs_info(lines, data)

        # ====================
        # replace lines
        repmap = self.replacer.create_repmap(names_dict)
        rep_lines = self.replacer.replace_names_in_terms(lines, repmap)

        # ====================
        # make a directory for export
        # and the directory path is embedded to a rust code.
        self.exporter.setup_env()
        self.dirpath = self.exporter.mkdir_new_res("Opt_")

        # ====================
        # assemble string parts into one code
        code = self.writer.write_code(rep_lines, self.dirpath)

        # ====================
        # save a code string as main.rs
        self.exporter.create_main(code)

        if now:
            # execute command 'cargo run' or 'cargo run --release'
            self._execute(release)

            # read and return optimized results
            optres = self.reader.read(self.dirpath, unks_dict)
            return optres
