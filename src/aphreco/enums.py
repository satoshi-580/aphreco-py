import enum


class ItemType(enum.Flag):
    # Component
    P = enum.auto()  # a constant model parameter
    Y = enum.auto()  # a dependent variable
    R = enum.auto()  # a reference to another variable (proxy, shortcut to P)
    E = enum.auto()  # a provisional effect
    X = enum.auto()  # an unknown parameter in optimization
    I = enum.auto()  # an yp_index being set in coding
    A = enum.auto()  # a term alias to be replaced by a term
    VARIABLE = P | Y | R | E | X | I | A

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


class EqType(enum.Enum):
    ODE = enum.auto()
    REC = enum.auto()
    CRE = enum.auto()


class StepType(enum.Flag):
    Dopri45 = enum.auto()
    Rk4 = enum.auto()


class FminType(enum.Flag):
    NelderMead = enum.auto()
    GeneticAlgorithm = enum.auto()
