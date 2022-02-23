import enum


class ItemType(enum.Flag):
    # Component
    Y = enum.auto()  # a dependent variable
    P = enum.auto()  # a constant model parameter
    X = enum.auto()  # an unknown parameter in optimization
    E = enum.auto()  # a provisional effect
    A = enum.auto()  # an alias (or a placeholder) of a term to be replaced
    R = enum.auto()  # a reference to another variable (proxy, shortcut to P)
    VARIABLE = Y | P | X | R | E | A

    CON = enum.auto()  # continuous edge
    REG = enum.auto()  # discrete edge with a regular interval
    FLX = enum.auto()  # discrete edge with a flexible interval
    STR = enum.auto()  # inline string for customizing processes
    EDGE = CON | REG | FLX | STR

    COMPONENT = VARIABLE | EDGE

    # Composite
    MODEL = enum.auto()  # a model with children listed as tree structure

    # Item
    ITEM = COMPONENT | MODEL


class FnType(enum.Enum):
    ODE = enum.auto()
    REC = enum.auto()
    CRE = enum.auto()


class StepType(enum.Flag):
    Dopri45 = enum.auto()
    Rk4 = enum.auto()


class FminType(enum.Flag):
    NelderMead = enum.auto()
    GeneticAlgorithm = enum.auto()
