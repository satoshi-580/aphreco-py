from typing import Dict, Set, Tuple

import sympy
from aphreco.core.base import BaseComponent, BaseEdge, BaseItem
from aphreco.enums import ItemType

from .symbolize import extract_symset, str_symbol_name


class ImplCollectForVariable(BaseComponent):
    def collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        names_dict[self.name] = (self.type, -1)
        return names_dict

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        if self.term is None:
            return used_names_set
        else:
            used_names: Set[str] = set()

            symbols_set = sympy.sympify(self.term).atoms(sympy.Symbol)
            str_symbols_set = {str(symbol) for symbol in symbols_set}
            used_names = used_names | str_symbols_set

            return used_names_set | used_names

    def collect_values(self, vals_dict):
        vals_dict[self.name] = self.value
        return vals_dict


class ImplCollectForCon(BaseEdge):
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

    def collect_terms(self):
        pass


class ImplCollectForReg(BaseEdge):
    def collect_names(self, _):
        pass

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        """collects all names used in terms and a beat of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        # beat
        used_names = {name for name in self.beat}
        # terms
        for yname, term in self.term.items():
            used_names.add(str_symbol_name(yname))
            symset = extract_symset(term)
            used_names = used_names | symset

        return used_names_set | used_names

    def collect_values(self):
        pass

    def collect_terms(self):
        pass


class ImplCollectForModel(BaseItem):
    def collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        """recursively collects names of Y, P, X, E in lower layers than the current model.

        This method is an abstractmethod defined in and forced by BaseItem.
        Variable and Edge classes also have this method.
        The names collected in this method does not collect Model.name,
        because Model.name is not needed to be unique in a whole tree;
        Duplication of Model.names in a whole tree does not matter as long as
        it is unique within a single model.

        Args:
            names_dict (OrderedDict[str, (ItemType, int)]): The argument in which
                the function collects and stores tree items.
                The key of this dictionary indicates the name of Variable (str), and
                the value of this dictionary is a tuple of ItemType and index in Y or P.
                All indices are set to -1 in the collection phase and
                will be update in replacement phase.
        """
        if len(self.children) == 0:
            return names_dict

        for _, item in self.children.items():
            # does not collect from Edge
            if isinstance(item, BaseEdge):
                continue

            # collect from Variable, or go to lower Model
            names_dict = item.collect_names(names_dict)
        return names_dict
