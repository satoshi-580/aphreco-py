from aphreco.enums import SimType

from .base import BaseStepMethod


class Rk4(BaseStepMethod):
    def __init__(self, **options):
        self.simtype = SimType.Dopri45
        self.is_default = True
        self.options = {
            "h": 1e-3,
        }

        if options:
            self.set_options(options=options)
