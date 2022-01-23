from .simulate.base import BaseStepMethod
from .simulate.dopri45 import Dopri45


class Simulator:
    def __init__(
        self,
        stepper: BaseStepMethod = Dopri45(),
    ):
        if isinstance(stepper, BaseStepMethod):
            self.stepper = stepper
        else:
            raise TypeError("invalid stepper type")

    def collect_method_and_options(self):
        for method in self.methods:
            print(method.write_options)
