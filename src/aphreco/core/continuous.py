from collections import OrderedDict
from typing import Dict, List, Optional

from aphreco.enums import ItemType

from .base import BaseEdge
from .func.collect import ImplCollectForCon
from .func.rename import rename_all
from .func.symbolize import extract_symset


class Con(ImplCollectForCon, BaseEdge):
    def __init__(
        self,
        term: Dict[str, str],
        name: str = None,
        _is_default_name: bool = None,
    ):
        self.term = term
        self._type = ItemType.CON
        self.parent = None

        if name is None:
            self._name = self._create_name_from_term(term)
            if _is_default_name is None:
                _is_default_name = True
        else:
            self._name = name
            if _is_default_name is None:
                _is_default_name = False

        self._is_default_name = _is_default_name

    @property
    def type(self):
        return self._type

    def _create_name_from_term(self, term):
        str_from = ""
        str_to = ""
        for name, term in term.items():
            if term.lstrip()[0] == "-":
                str_from += "deriv_" + name + "=" + term + ","
            else:
                str_to += "deriv_" + name + "=" + term + ","
        name = f"{str_from[:-1]} -> {str_to[:-1]}"
        name = name.strip()
        return name

    def _add_or_skip(self, parent, is_done):
        edge = Con(
            term=self.term,
            name=self.name,
            _is_default_name=self._is_default_name,
        )
        edge.parent = parent
        return edge, is_done

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
            _is_default_name=self._is_default_name,
        )
        return copied_edge

    def _rename_self(self, repmap: Dict[str, str]):
        if not self._is_default_name:
            if self._name in repmap.keys():
                self._name = repmap[self._name]

        renamed_term = self.term.copy()
        for yname in self.term.keys():
            # extract a set of symbols (names) from a term
            # filter the set to be replaced.
            symset = extract_symset(renamed_term[yname])
            intersect = symset & repmap.keys()

            # replace all positions in a term while other inclusive names
            # are not replaced. For example, when replacing 'X0', neither
            # 'prefix_X0' nor 'X0_suffix' will be replaced.
            if intersect != set():
                for old in intersect:
                    renamed_term[yname] = rename_all(
                        term=renamed_term[yname],
                        old=old,
                        new=repmap[old],
                    )

            if yname in repmap.keys():
                new_name = repmap[yname]
                renamed_term[new_name] = renamed_term[yname]
                del renamed_term[yname]
        self.term = renamed_term

        if self._is_default_name:
            self._name = self._create_name_from_term(self.term)

        return self

    def _delete_involved(self, name: str):
        del_term = self.term.copy()
        for yname in self.term.keys():
            # if name is included as a symbol in term,
            # the whole term is deleted.
            symset = extract_symset(del_term[yname])
            if name in symset:
                del del_term[yname]

        if name in del_term.keys():
            del del_term[name]

        self.term = del_term
        if len(self.term) > 0:
            is_empty = False
        else:
            is_empty = True

        if self._is_default_name and (not is_empty):
            self._name = self._create_name_from_term(self.term)

        return is_empty, self


# class EdgeC(BaseEdge):
#     def _get_symbols(self):
#         symbols = set()
#         for k, term in self.term.items():
#             symbols.add(sympy.sympify(k))
#             symbols = symbols.union(sympy.sympify(term).atoms(sympy.Symbol))
#         return symbols

#     def _formulate(self, eq_dicts):
#         dict_ode = eq_dicts["ode"]

#         for key, term in self.term.items():
#             if key not in dict_ode.keys():
#                 dict_ode[key] = term
#             else:
#                 dict_ode[key] += f" + {term}"

#         eq_dicts["ode"] = dict_ode
#         return eq_dicts
