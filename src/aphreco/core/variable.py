from collections import deque
from typing import Optional, Tuple

import sympy
from aphreco.core.base import BaseComponent, ItemType

VTYPES = {
    "y": ItemType.Y,  # dependent variable
    "p": ItemType.P,  # model parameter (independent, constant)
    "x": ItemType.X,  # unknown parameter (optimized)
}


class Var(BaseComponent):
    def __init__(
        self,
        name: str,
        value: float = 0.0,
        vtype: str = "y",
        term: Optional[str] = None,
    ):
        self.name = name
        self.type = vtype
        if term is not None:
            if self.type != ItemType.Y:
                raise ValueError(
                    f"cre term is only for a dependent variable: {self.type}"
                )

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


class Y(BaseComponent):
    def __new__(
        cls,
        name: str,
        value: float = 0.0,
        term: Optional[str] = None,
    ):
        return Var(name=name, value=value, vtype="y", term=term)


class P(BaseComponent):
    def __new__(
        cls,
        name: str,
        value: float = 0.0,
        bounds: Optional[Tuple[float, float]] = None,
    ):
        return Var(name=name, value=value, vtype="p", term=None)
