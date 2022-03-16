from collections import OrderedDict
from typing import Dict, List, Optional, Set

from aphreco.enums import ItemType
from aphreco.types import OdeTerm, TermsDicts

from .base import BaseEdge
from .func.rename import create_name_from_term, rename_all
from .func.symbolize import extract_symset, str_symbol_name

ODE_PREFIX = "deriv_"
ODE_RELATION = "="


class BaseCon(BaseEdge):
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, term: OdeTerm):
        self._term = term


class ImplCollectForCon(BaseCon):
    def collect_names(self, _):
        pass

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        """collects all names used in terms of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        used_names = set()
        for yname, term in self.term.items():
            used_names.add(str_symbol_name(yname))

            symset = extract_symset(term)
            used_names = used_names | symset

        return used_names_set | used_names

    def collect_values(self, vals_dict):
        return vals_dict

    def collect_terms(self, terms_dict: TermsDicts) -> TermsDicts:
        ode = terms_dict[0]

        for yname, rhs in self.term.items():
            if yname not in ode.keys():
                ode[yname] = [rhs]
            else:
                ode[yname].append(rhs)

        return (ode, terms_dict[1], terms_dict[2])


class ImplRenameForCon(BaseCon):
    def _rename_self(self, repmap: Dict[str, str]):
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
            self._name = create_name_from_term(self.term, ODE_PREFIX, ODE_RELATION)

        return self


class Con(ImplCollectForCon, ImplRenameForCon, BaseEdge):
    def __init__(
        self,
        term: OdeTerm,
        name: str = None,
        _is_default_name: bool = None,
    ):
        self.term = term
        self._type = ItemType.CON
        self.parent = None

        if name is None:
            self._name = create_name_from_term(self.term, ODE_PREFIX, ODE_RELATION)
            if _is_default_name is None:
                _is_default_name = True
        else:
            self._name = name
            if _is_default_name is None:
                _is_default_name = False

        self._is_default_name = _is_default_name

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
        _is_top: bool = False,
    ):
        copied_term: OdeTerm = OrderedDict()
        for yname, str_rhs in self.term.items():
            # because lhs is always ItemType.Y,
            # add prefix/suffix to yname unconditionally.
            copied_name = prefix + yname + suffix

            copied_rhs = str_rhs
            if _repmap is not None:
                for old, new in _repmap.items():
                    copied_rhs = rename_all(copied_rhs, old, new)

            copied_term[copied_name] = copied_rhs

        if self.name != create_name_from_term(self.term, ODE_PREFIX, ODE_RELATION):
            copied_name = self.name
        else:
            copied_name = None

        copied_edge = Con(
            term=copied_term,
            name=copied_name,
            _is_default_name=self._is_default_name,
        )
        return copied_edge

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
            self._name = create_name_from_term(self.term, ODE_PREFIX, ODE_RELATION)

        return is_empty, self
