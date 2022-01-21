import enum
from typing import List, Union


class OptMethod(enum.Flag):
    NelderMead = enum.auto()
    GeneticAlgorithm = enum.auto()
    Single = NelderMead
    Parallel = GeneticAlgorithm


class OptOptions:
    def __init__(self):
        pass


class Optimizer:
    def __init__(
        self,
        method: Union[OptMethod, List[OptMethod]] = OptMethod.NelderMead,
        options: OptOptions = OptOptions(),
    ):
        self.method = method
        self.options = options
