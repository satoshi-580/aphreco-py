from aphreco.enums import OptType

from .base import BaseOptimizeMethod


class NelderMead(BaseOptimizeMethod):
    def __init__(self, **options):
        self.name = "NelderMead"
        self.opttype = OptType.NelderMead
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
