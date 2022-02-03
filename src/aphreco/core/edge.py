from collections import OrderedDict
from typing import Dict, List, Optional, Set, Tuple

import sympy
from aphreco.enums import ItemType

from .base import BaseEdge


class Con(BaseEdge):
    def __init__(self, term: Dict[str, str], name=None):
        self.term = term
        self._type = ItemType.CON
        self.parent = None

        if name is not None:
            self.name = name
        else:
            self.name = self._create_name_from_term(term)

    @property
    def type(self):
        return self._type

    def _create_name_from_term(self, term):
        str_from = ""
        str_to = ""
        for name, term in term.items():
            if term.lstrip()[0] == "-":
                str_from += name + ":" + term + ","
            else:
                str_to += name + ":" + term + ","
        name = f"{str_from[:-1]} -> {str_to[:-1]}"
        return name

    def _add_or_skip(self, parent, is_done):
        edge = Con(
            term=self.term,
            name=self.name,
        )
        edge.parent = parent
        return edge, is_done

    def _collect_names(self, _):
        pass

    def _collect_names_in_terms_recursively(self, used_names_set: Set[str]):
        """collects all names used in terms of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        used_names = set()
        for yname, term in self.term.items():
            used_names.add(str(sympy.sympify(yname)))

            symbols_set = sympy.sympify(term).atoms(sympy.Symbol)
            str_symbols_set = {str(symbol) for symbol in symbols_set}
            used_names = used_names | str_symbols_set

        return used_names_set | used_names

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        structure.append(f"{indent}[{self.type.name}] {self.name}")
        return structure

    def copy(
        self,
        prefix="",
        suffix="",
        exclusive: List[str] = [],
        share: bool = False,
        _repmap: Dict[str, str] = None,
    ):
        copied_term: Dict[str, str] = OrderedDict()
        for yname, str_rhs in self.term.items():
            # because lhs is always ItemType.Y,
            # add prefix/suffix to yname unconditionally.
            copied_name = prefix + yname + suffix

            copied_rhs = str_rhs
            if _repmap is not None:
                for old, new in _repmap.items():
                    copied_rhs = copied_rhs.replace(old, new)

            copied_term[copied_name] = copied_rhs

        if self.name != self._create_name_from_term(self.term):
            copied_name = self.name
        else:
            copied_name = None

        copied_edge = Con(
            term=copied_term,
            name=copied_name,
        )
        return copied_edge

    def collect_eq(self):
        pass

    def collect_val(self):
        pass


class Reg(BaseEdge):
    """Reg represents a edge item connecting Y variables in a model.

    Attributes:
        beat (str, str, str): The tuple of three parameter names (start, stop, step),
            which defines discrete time points the edge term is calculated.

        term Dict[str, str]: The lhs and rhs of a recursive (difference) equation in a model.
            The key and value of the dictionary indicate a name of dependent variable (y) and
            a difference occuring at a discrete point (delta_y), respectively.

        name (str): The name of edge item in a model. If it is not designated in instanciation,
            it is automatically created from term.

        type (ItemType): The type of RegularBeat Edge ItemType.REG.

        parent (Model): The parent item.
    """

    def __init__(
        self,
        beat: Tuple[str, str, str],
        term: Dict[str, str],
        name: str = None,
    ):
        self.beat = beat
        self.term = term
        self._type = ItemType.REG
        self.parent = None

        if name is not None:
            self.name = name
        else:
            self.name = self._create_name_from_term(term)

    @property
    def type(self):
        return self._type

    def _create_name_from_term(self, term):
        str_from = ""
        str_to = ""
        for name, term in term.items():
            if term.lstrip()[0] == "-":
                str_from += name + ":" + term + ","
            else:
                str_to += name + ":" + term + ","
        name = f"{str_from[:-1]} -> {str_to[:-1]}"
        return name

    def _add_or_skip(self, parent, is_done):
        edge = Reg(
            beat=self.beat,
            term=self.term,
            name=self.name,
        )
        edge.parent = parent
        return edge, is_done

    def _collect_names(self, _):
        pass

    def _collect_names_in_terms_recursively(self, used_names_set: Set[str]):
        """collects all names used in terms and a beat of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        # beat
        used_names = {name for name in self.beat}
        # terms
        for yname, term in self.term.items():
            used_names.add(str(sympy.sympify(yname)))

            symbols_set = sympy.sympify(term).atoms(sympy.Symbol)
            str_symbols_set = {str(symbol) for symbol in symbols_set}
            used_names = used_names | str_symbols_set

        return used_names_set | used_names

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        structure.append(f"{indent}[{self.type.name}] {self.name}")
        return structure

    def copy(
        self,
        prefix="",
        suffix="",
        exclusive: List[str] = [],
        share: bool = False,
        _repmap: Dict[str, str] = None,
    ):
        # beat
        start, stop, step = self.beat
        if _repmap is not None:
            if start in _repmap.keys():
                start = _repmap[start]
            if stop in _repmap.keys():
                stop = _repmap[stop]
            if step in _repmap.keys():
                step = _repmap[step]
        copied_beat = (start, stop, step)

        # term
        copied_term: Dict[str, str] = OrderedDict()
        for yname, str_rhs in self.term.items():
            # because lhs is always ItemType.Y,
            # add prefix/suffix to yname unconditionally.
            copied_name = prefix + yname + suffix

            copied_rhs = str_rhs
            if _repmap is not None:
                for old, new in _repmap.items():
                    copied_rhs = copied_rhs.replace(old, new)

            copied_term[copied_name] = copied_rhs

        if self.name != self._create_name_from_term(self.term):
            copied_name = self.name
        else:
            copied_name = None

        copied_edge = Reg(
            beat=copied_beat,
            term=copied_term,
            name=copied_name,
        )

        return copied_edge

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
