import enum


class ItemType(enum.Flag):
    # Component
    Y = enum.auto()  # dependent variable
    P = enum.auto()  # constant model parameter
    X = enum.auto()  # unknown parameter in optimization
    E = enum.auto()
    VARIABLE = Y | P | X | E

    CON = enum.auto()  # continuous edge
    REG = enum.auto()  # discrete edge with a regular interval
    EDGE = CON | REG

    COMPONENT = VARIABLE | EDGE

    # Composite
    MODEL = enum.auto()  # show inside

    # Item
    ITEM = COMPONENT | MODEL
