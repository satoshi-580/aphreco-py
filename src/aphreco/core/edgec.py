from collections import deque
from typing import Dict

import sympy
from aphreco.types import ItemType

from .base import BaseEdge


class EdgeC(BaseEdge):
    def __init__(self, term: Dict[str, str]):
        self.term = term
        self._type = ItemType.CON
        self.name = term

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, etype: ItemType):
        raise AttributeError("edge type is immutable.")

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, term):
        str_from = ""
        str_to = ""
        for name, term in self.term.items():
            if term.lstrip()[0] == "-":
                str_from += name + ":" + term + ","
            else:
                str_to += name + ":" + term + ","
        self._name = f"{str_from[:-1]}->{str_to[:-1]}"

    def _get_symbol(self):
        symbols = set()
        for k, term in self.term.items():
            symbols.add(sympy.sympify(k))
            symbols = symbols.union(sympy.sympify(term).atoms(sympy.Symbol))
        return symbols

    def __str__(self):
        return f"{self.name}[{self.type.name}]"

    def _print_tree(self, indent=""):
        print(f"{indent}{self}")

    def _formulate(self, eq_dicts):
        dict_ode = eq_dicts["ode"]

        for key, term in self.term.items():
            if key not in dict_ode.keys():
                dict_ode[key] = term
            else:
                dict_ode[key] += f" + {term}"

        eq_dicts["ode"] = dict_ode
        return eq_dicts

    def _remove_by_name(self, dq_path: deque):
        pass
