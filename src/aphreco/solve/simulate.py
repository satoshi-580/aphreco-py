import enum


class SimMethod(enum.Flag):
    Rk4 = enum.auto()
    Dopri45 = enum.auto()


class SimOptions:
    def __init__(self):
        pass


class Simulator:
    def __init__(
        self,
        method: SimMethod = SimMethod.Dopri45,
        options: SimOptions = SimOptions(),
    ):
        self.method = method
        self.options = options
