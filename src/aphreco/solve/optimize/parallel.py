from aphreco.enums import OptType

from .base import BaseOptimizeMethod


class GeneticAlgorithm(BaseOptimizeMethod):
    def __init__(self, **options):
        self.opttype = OptType.GeneticAlgorithm
        self.is_default = True
        self.options = {
            "max_gen": 0,
            "n_pop": 10,
            "mutation_rate": 1e-6,
            "verbose": False,
        }

        if options:
            self.set_options(options=options)
