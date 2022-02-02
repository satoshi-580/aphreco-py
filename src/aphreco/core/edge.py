from typing import Dict, List, Optional, Tuple

from aphreco.enums import ItemType

from .base import BaseEdge


class Con(BaseEdge):
    cnt = 0

    def __init__(self, term: Dict[str, str], name=None):
        self.term = term
        self._type = ItemType.CON
        self.parent = None

        if name is not None:
            self.name = name
        else:
            Con.cnt += 1
            self.name = "con_edge_" + str(Con.cnt)

    @property
    def type(self):
        return self._type

    def _add_or_skip(self, parent, is_done):
        edge = Con(
            term=self.term,
            name=self.name,
        )
        edge.parent = parent
        return edge, is_done

    def _collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        return names_dict

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        structure.append(
            f"{indent}{self.name}[{self.type.name}]{set(self.term.keys())}"
        )
        return structure

    def copy(self, prefix="", suffix="", exclusive=[], share=False):
        copied_edge = Con(
            term=self.term,
            name=self.name,
        )
        return copied_edge

    def collect_eq(self):
        pass

    def collect_val(self):
        pass


class Reg(BaseEdge):
    def collect_eq(self):
        pass

    def collect_val(self):
        pass


# from collections import deque
# from typing import Dict

# import sympy
# from aphreco.enums import ItemType

# from ..base import BaseEdge


# class EdgeC(BaseEdge):
#     def __init__(self, term: Dict[str, str]):
#         self.term = term
#         self._type = ItemType.CON
#         self.name = term

#     @property
#     def type(self):
#         return self._type

#     @type.setter
#     def type(self, etype: ItemType):
#         raise AttributeError("edge type is immutable.")

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, term):
#         str_from = ""
#         str_to = ""
#         for name, term in self.term.items():
#             if term.lstrip()[0] == "-":
#                 str_from += name + ":" + term + ","
#             else:
#                 str_to += name + ":" + term + ","
#         self._name = f"{str_from[:-1]}->{str_to[:-1]}"

#     def _get_symbols(self):
#         symbols = set()
#         for k, term in self.term.items():
#             symbols.add(sympy.sympify(k))
#             symbols = symbols.union(sympy.sympify(term).atoms(sympy.Symbol))
#         return symbols

#     def _print_tree(self, indent=""):
#         print(f"{indent}{self}[{self.type.name}]")

#     def _formulate(self, eq_dicts):
#         dict_ode = eq_dicts["ode"]

#         for key, term in self.term.items():
#             if key not in dict_ode.keys():
#                 dict_ode[key] = term
#             else:
#                 dict_ode[key] += f" + {term}"

#         eq_dicts["ode"] = dict_ode
#         return eq_dicts

#     def _remove_by_name(self, dq_path: deque):
#         pass


# from collections import OrderedDict, deque
# from typing import Dict, Tuple

# import sympy
# from aphreco.enums import ItemType

# from ..base import BaseComponent


# class EdgeR(BaseEdge):
#     def __init__(self, beat: Tuple[str, str, str], term: Dict[str, str]):
#         """
#         term: Dict[lhs, rhs]
#             lhs indicates a dependent variable.
#             rhs is the difference of the corresponding lhs
#             at a discrete point (delta_lhs += rhs).
#         beat: Tuple(start, stop, step)
#         """
#         self.term = term
#         self.beat = beat
#         self._type = ItemType.REG
#         self.name = term

#     @property
#     def type(self):
#         return self._type

#     @type.setter
#     def type(self, etype: ItemType):
#         raise AttributeError("edge type is immutable.")

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, term):
#         str_from = ""
#         str_to = ""
#         for name, term in self.term.items():
#             if term.lstrip()[0] == "-":
#                 str_from += name + ":" + term + ","
#             else:
#                 str_to += name + ":" + term + ","
#         self._name = f"{str_from[:-1]}->{str_to[:-1]}"

#     def _get_symbols(self):
#         symbols = set()

#         for b in self.beat:
#             symbols.add(sympy.sympify(b))

#         for k, term in self.term.items():
#             symbols.add(sympy.sympify(k))
#             symbols = symbols.union(sympy.sympify(term).atoms(sympy.Symbol))
#         return symbols

#     def _print_tree(self, indent=""):
#         print(f"{indent}{self}[{self.type.name}]")

#     def _formulate(
#         self,
#         eq_dicts: Dict[str, Dict],
#     ):
#         dict_rec = eq_dicts["rec"]

#         if self.beat not in dict_rec.keys():
#             dict_rec[self.beat] = OrderedDict()

#         for key, term in self.term.items():
#             if key not in dict_rec[self.beat].keys():
#                 dict_rec[self.beat][key] = term
#             else:
#                 dict_rec[self.beat][key] += f" + {term}"

#         eq_dicts["rec"] = dict_rec
#         return eq_dicts

#     def _remove_by_name(self, dq_path: deque):
#         pass
