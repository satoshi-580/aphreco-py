from aphreco.enums import StepType

from .base import BaseStepMethod


class Rk4(BaseStepMethod):
    def __init__(self, **options):
        self.is_default = True
        self.options = {
            "h": 1e-3,
        }

        if options:
            self.set_options(**options)

    @property
    def name(self):
        return StepType.Rk4.name

    @property
    def type(self):
        return StepType.Rk4
