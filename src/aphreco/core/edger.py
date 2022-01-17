from collections import OrderedDict, deque
from typing import Dict, Tuple

import sympy
from aphreco.core.base import BaseEdge, ItemType


class EdgeR(BaseEdge):
    def __init__(self, beat: Tuple[str, str, str], term: Dict[str, str]):
        """
        term: Dict[lhs, rhs]
            lhs indicates a dependent variable.
            rhs is the difference of the corresponding lhs
            at a discrete point (delta_lhs += rhs).
        beat: Tuple(start, stop, step)
        """
        self.term = term
        self.beat = beat
        self._type = ItemType.REG
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

    def _formulate(
        self,
        eq_dicts: Dict[str, Dict],
    ):
        dict_rec = eq_dicts["rec"]

        if self.beat not in dict_rec.keys():
            dict_rec[self.beat] = OrderedDict()

        for key, term in self.term.items():
            if key not in dict_rec[self.beat].keys():
                dict_rec[self.beat][key] = term
            else:
                dict_rec[self.beat][key] += f" + {term}"

        eq_dicts["rec"] = dict_rec
        return eq_dicts

    def _remove_by_name(self, dq_path: deque):
        pass
