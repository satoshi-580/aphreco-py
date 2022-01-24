from aphreco.enums import SimType

from .base import BaseStepMethod


class Dopri45(BaseStepMethod):
    def __init__(self, **options):
        self.name = "Dopri45"
        self.simtype = SimType.Dopri45
        self.is_default = True
        self.options = {
            "h0": 1e-5,
            "abstol": 1e-6,
            "reltol": 1e-6,
            "hmin": 1e-7,
            "hmax": 1e-3,
        }

        if options:
            self.set_options(**options)
