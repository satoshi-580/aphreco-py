from collections import deque

import sympy
from aphreco.core.base import BaseComponent, ItemType

VTYPES = {
    "y": ItemType.Y,  # dependent variable
    "p": ItemType.P,  # model parameter (independent, constant)
    "x": ItemType.X,  # unknown parameter (optimized)
}


class Var(BaseComponent):
    def __init__(self, name: str, vtype: str = "y", value: float = 0.0):
        self.name = name
        self.type = vtype

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, vtype: str):
        if vtype not in VTYPES.keys():
            raise ValueError(
                f"invalid variable type: {vtype} \
                \nvtype must be chosen from {tuple(VTYPES.keys())}"
            )
        self._type = VTYPES[vtype]

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    def _get_symbol(self):
        return sympy.sympify(self.name)

    def __str__(self):
        return f"{self.name}[{self.type.name}]"

    def _print_tree(self, indent=""):
        print(f"{indent}{self}")

    def _remove_by_name(self, dq_path: deque):
        pass
