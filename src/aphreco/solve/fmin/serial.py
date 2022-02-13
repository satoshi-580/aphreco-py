from aphreco.enums import FminType

from .base import BaseFminAlgorithm


class NelderMead(BaseFminAlgorithm):
    def __init__(self, **options):
        self._name = "NelderMead"
        # self.opttype = OptType.NelderMead
        self.is_default = True
        self.options = {
            "max_iter": 0,
            "adaptive": True,
            "x_abstol": 1e-6,
            "f_abstol": 1e-6,
            "verbose": False,
        }

        if options:
            self.set_options(**options)

    @property
    def name(self):
        return FminType.NelderMead.name

    @property
    def type(self):
        return FminType.NelderMead
