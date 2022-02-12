from typing import Dict, List, Optional, Set, Tuple, Union

import sympy
from aphreco.enums import ItemType

from .base import BaseComponent
from .func.rename import rename_all
from .func.symbolize import extract_symset

VTYPES = {
    "y": ItemType.Y,  # dependent variable
    "p": ItemType.P,  # model parameter (independent and constant)
    "x": ItemType.X,  # unknown parameter (independent and optimized)
    "e": ItemType.E,  # provisional effect
    "a": ItemType.A,  # an alias (or a placeholder) of a term to be replaced
    "r": ItemType.R,  # reference to another variable (generated in skipping copy)
}


class BaseVariable(BaseComponent):
    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type: Union[str, ItemType]):
        if isinstance(type, ItemType):
            self._type = type
        else:
            if type not in VTYPES.keys():
                raise ValueError(
                    f"invalid variable type: {type} \
                    \nvtype must be chosen from {tuple(VTYPES.keys())}"
                )

            self._type = VTYPES[type]

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value


class ImplCollectForVariable(BaseVariable):
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

    def collect_values(self, vals_dict: Dict[str, float]) -> Dict[str, float]:
        vals_dict[self.name] = self.value
        return vals_dict

    def collect_terms(self, terms_dict: Dict[str, Dict]) -> Dict[str, Dict]:
        if self.term is None:
            return terms_dict

        cre = terms_dict["cre"]

        if self.name not in cre.keys():
            cre[self.name] = self.term
        else:
            raise ValueError(
                f"multiple CREs was found for a single variable '{self.name}'."
            )

        terms_dict["cre"] = cre
        return terms_dict


class ImplRenameForVariable(BaseVariable):
    def _rename_self(self, repmap: Dict[str, str]):
        if self.name in repmap.keys():
            self._name = repmap[self.name]

        if self.term is not None:
            symset = extract_symset(self.term)
            intersect = symset & repmap.keys()

            if intersect != set():
                for old in intersect:
                    self.term = rename_all(
                        term=self.term,
                        old=old,
                        new=repmap[old],
                    )
        return self


class Variable(ImplCollectForVariable, ImplRenameForVariable, BaseVariable):
    """Variable represents a dependent/independent variable in a model.

    Attributes:
        name (str): The name of variable used as a symbol in equations

        value (float): The value of Variable object, which means
            initial state in simulation for y,
            constant and fixed parameter for p,
            initial value in optimization for x, and
            excluded and non-effect value in filtration for e.

        type (Union[str, ItemType]): The type of Variable that is any of ItemType.Y, P, X, E.
            In constructor, designate as a string of "y", "p", "x", or "e".

        bounds (float, float): The lower and upper bounds of the Variable value
            that are used in optimization.

        term (str): The right hand side of constant relationship.

        share (bool): if share this variable name or not in Model.copy.
            if False, a copied variable adds prefix or suffix to the name.
            if True, not add any prefix or suffix meaning the same name is used in another model.
    """

    def __init__(
        self,
        name,
        value=0.0,
        type: Union[str, ItemType] = "y",
        bounds=None,
        term=None,
        share=True,
    ):
        self._name = name
        self.value = float(value)
        self.type = type
        self.share = share
        self.parent = None

        # bounds for optimization for type "p"
        if bounds is None:
            self.bounds = None
        else:
            self.bounds = (float(bounds[0]), float(bounds[1]))

        # term is only for CRE (constant relationship)
        if term is None:
            self.term = None
        else:
            if self.type != ItemType.Y:
                raise ValueError(
                    f"variable type must be 'y' when cre term is used: {self.type}"
                )
            self.term = term

    def _add_or_skip(self, parent, is_done):
        if is_done is not None and is_done[self.name]:
            # if duplicate == "error", is_done is None.
            # in this case, duplicate == "skip".
            #
            # is_done[self.name] is True,
            # another item with the same name has already been added,
            # therefore this item should be skipped.
            return None, is_done

        var = Variable(
            name=self.name,
            value=self.value,
            type=self.type,
            bounds=self.bounds,
            term=self.term,
            share=self.share,
        )
        var.parent = parent

        if is_done is not None:
            is_done[var.name] = True  # skip this name next time

        return var, is_done

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        if self.term is None:
            str_tree = f"{indent}[ {self.type.name} ] {self}"
        else:
            str_tree = f"{indent}[ {self.type.name} ] {self} = {self.term}"

        structure.append(str_tree)
        return structure

    def copy(
        self,
        prefix="",
        suffix="",
        exclusive: List[str] = [],
        share: bool = False,
        _repmap: Optional[Dict[str, str]] = None,
        _is_top: bool = False,
    ):
        copied_name = self.name
        copied_term = self.term

        if _repmap is not None:
            if self.name in _repmap.keys():
                copied_name = _repmap[self.name]

            # replace names in term
            if copied_term is not None:
                symbols_set = sympy.sympify(copied_term).atoms(sympy.Symbol)
                str_symbols_set = {str(symbol) for symbol in symbols_set}
                intersect = str_symbols_set & _repmap.keys()
                if intersect != set():
                    for old in intersect:
                        copied_term = rename_all(
                            term=copied_term,
                            old=old,
                            new=_repmap[old],
                        )

        copied_var = Variable(
            name=copied_name,
            value=self.value,
            type=self.type,
            bounds=self.bounds,
            term=copied_term,
            share=self.share,
        )
        return copied_var

    def _delete_involved(self, name: str):
        if (self.term is not None) and (name in self.term):
            self.term = None
            if self.type in (ItemType.Y | ItemType.E | ItemType.A):
                return True, self

        return False, self


class Y:
    def __new__(
        cls,
        name: str,
        value: float = 0.0,
        term: Optional[str] = None,
    ):
        """Y class is for defining a dependent variable.

        If the argument 'term' is designated, the term will be evaluated as a constant relationship (CRE).
        For example, if defining Y(name="C0", term="X0 / V0"), aphreco regard a relationship
        'C0 = X0 / V0' as constant, and calculate the equation every step of simulation.
        Please note that it is not recommended to use 'C0' in Edge terms when the name is defined
        as the lhs of CRE. In the case that use a temporary name in edge term, define as A (an alias of a term).

        Returns:
            Variable: The variable object with its type set to ItemType.Y.
        """
        return Variable(name=name, value=value, type="y", term=term, share=False)


class P:
    def __new__(
        cls,
        name: str,
        value: float = 0.0,
        share: bool = True,
    ):
        """P class is for defining an independent parameter in a model.

        If shared, ***???***
        Variable.term is not evaluated.

        Returns:
            Variable: The variable object with its type set to ItemType.P.
        """
        return Variable(name=name, value=value, type="p", term=None, share=share)


class X(BaseComponent):
    def __new__(
        cls,
        name: str,
        value: float = 0.0,
        bounds: Optional[Tuple[float, float]] = None,
    ):
        """X class is for defining an unknown parameter in optimization.

        X variable is regarded as an unknown parameter in optimization, whereas it is
        regarded as a fix parameter (like a P variable) in simulation.

        Variable.term is not evaluated.

        Returns:
            Variable: The variable object with its type set to ItemType.X.
        """
        return Variable(name=name, value=value, type="x", term=None, bounds=bounds)


class A:
    def __new__(
        cls,
        name: str,
        term: str,
        share: bool = True,
    ):
        """A class is for defining an alias of a term which is to be replaced.

        In writing a model code, the name of A is replaced by its term.
        For example, if a name 'J0' is defined with a term 'Jmax * C0 / (Km_ + C0)',
        the 'J0' in edge terms in a model will be replaced by the term in writing
        a model code.

        Variable.value is not evaluated.

        Returns:
            Variable: The variable object with its type set to ItemType.A.
        """
        return Variable(name=name, type="a", term=term, share=share)
