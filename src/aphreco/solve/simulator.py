from collections import OrderedDict
from pathlib import Path
from typing import Dict

from aphreco.core import Model

from .base import BaseSolver
from .command import Command
from .export import Exporter
from .format import SimFormatter
from .read import SimResReader
from .replace import Replacer
from .step.base import BaseStepMethod
from .step.dopri45 import Dopri45
from .write import SimWriter


class Simulator(BaseSolver):
    def __init__(
        self,
        stepper: BaseStepMethod = Dopri45(),
        **options,
    ):
        if not isinstance(stepper, BaseStepMethod):
            raise TypeError("invalid stepper type")

        self.stepper = stepper
        if options:
            self.stepper.set_options(**options)

        self.formatter = SimFormatter()
        self.replacer = Replacer()
        self.exporter = Exporter()
        self.writer = SimWriter()
        self.command = Command()
        self.reader = SimResReader()

    def run(
        self,
        model: Model,
        smptime,
        now=True,
        release=False,
        simplify=False,
    ):
        """generate a simulation code and run it immediately.

        Args:
            model (Model): The model object.
            smptime Union[Tuple[float, float, float], List[float]]: The output times of simulation.
                A tuple is interpreted as (start, stop, step).
                A list is interpreted as a vector of time points.
            now (bool): Execute a generated code now if True.

        Returns:
            SimResult: The simulated result

        """
        # check args
        if not isinstance(model, Model):
            raise TypeError("invalid type: 'model'")

        if simplify:
            self.formatter.simplify_eq = True

        # ====================
        # dicts is a tuple of dictionaries (names_dict, vals_dict, terms_dicts).
        names_dict = model.set_yp_index(model.collect_names(OrderedDict()))
        vals_dict = model.collect_values(OrderedDict())
        terms_dicts = model.collect_terms((OrderedDict(), OrderedDict(), OrderedDict()))

        print("===Ode===")
        ore_dict = terms_dicts[0]
        for name in ore_dict.keys():
            print(name, ore_dict[name])

        print("\n===Rec===")
        for beat, recterms in terms_dicts[1].items():
            print("beat:", beat)
            for name, terms in recterms.items():
                print("  name:", name)
                for term in terms:
                    print("  ", term)

        print("\n===Cre===")
        cre_dict = terms_dicts[2]
        for name in cre_dict.keys():
            print(name, cre_dict[name])

        # ====================
        # format lines
        # generate lines with t/y/p/ode/rec/cond/beat/cre,
        # and lines of solver settings.
        lines = self.formatter.format_model_info((names_dict, vals_dict, terms_dicts))
        lines = self.formatter.format_simulator_info(lines, self)
        # unique lines: in the case of simulation, add the following keys,
        #     lines["smptime"]: sampling times
        lines = self.formatter.format_smptime_info(lines, smptime)

        # ====================
        # replace lines
        repmap = self.replacer.create_repmap(names_dict)
        rep_lines = self.replacer.replace_names_in_terms(lines, repmap)

        # ====================
        # make a directory for export
        # and the directory path is embedded to a rust code.
        self.exporter.setup_env()
        self.dirpath = self.exporter.mkdir_new_res("Sim_")

        # ====================
        # assemble string parts into one code
        code = self.writer.write_code(rep_lines, self.dirpath)

        # ====================
        # save a code string as main.rs
        self.exporter.create_main(code)

        if now:
            # execute command 'cargo run' or 'cargo run --release'
            self._execute(release)

            # read and return simulated results
            simres = self.reader.read(self.dirpath, model.ynames)
            return simres
