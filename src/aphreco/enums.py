import enum


class ProcType(enum.Flag):
    SIM = enum.auto()  # simulate
    OPT = enum.auto()  # optimize


class OptType(enum.Flag):
    NelderMead = enum.auto()
    GeneticAlgorithm = enum.auto()
    Serial = NelderMead
    Parallel = GeneticAlgorithm


class SimType(enum.Flag):
    Rk4 = enum.auto()
    Dopri45 = enum.auto()
    Step = Rk4 | Dopri45


class ItemType(enum.Flag):
    # Components
    Y = enum.auto()  # dependent variable
    P = enum.auto()  # constant model parameter
    X = enum.auto()  # unknown parameter in optimization
    VARIABLE = Y | P | X
    CON = enum.auto()  # continuous edge
    REG = enum.auto()  # discrete edge with a regular interval
    EDGE = CON | REG
    COMPONENT = VARIABLE | EDGE

    # Composite
    BOX = enum.auto()  # show inside
    BLACKBOX = enum.auto()  # hide inside if it has multiple type-Y objects
    MODEL = BOX | BLACKBOX
