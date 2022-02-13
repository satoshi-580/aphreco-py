from aphreco.enums import FminType

from .base import BaseFminAlgorithm


class GeneticAlgorithm(BaseFminAlgorithm):
    def __init__(self, **options):
        self.is_default = True
        self.options = {
            "max_gen": 100,
            "n_pop": 10,
            "mutation_rate": 0.8,
            "verbose": False,
        }

        if options:
            self.set_options(**options)

    @property
    def name(self):
        return FminType.GeneticAlgorithm.name

    @property
    def type(self):
        return FminType.GeneticAlgorithm
