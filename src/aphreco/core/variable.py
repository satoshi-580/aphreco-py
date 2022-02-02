from typing import Dict, List, Optional, Tuple, Union

from aphreco.enums import ItemType

from .base import BaseComponent

VTYPES = {
    "y": ItemType.Y,  # dependent variable
    "p": ItemType.P,  # model parameter (independent, constant)
    "x": ItemType.X,  # unknown parameter (optimized)
    # "e": ItemType.E,  # effect on a target
}


class Variable(BaseComponent):
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

    Example:
        >>> import aphreco as aph
        >>> var = aph.Variable("k", 0.01, "p")
        >>> var.name
        k
        >>> var.value
        0.01
        >>> var.type.name
        ItemType.P
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
        self.name = name
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

    def _collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        names_dict[self.name] = (self.type, -1)
        return names_dict

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        structure.append(f"{indent}{self}[{self.type.name}]")
        return structure

    def copy(self, prefix="", suffix="", exclusive=[], share=False):
        # TODO: how should the method deal with the case that the name
        # resulting from addition of prefix/suffix could be the same as
        # another existing name?
        if self.type == ItemType.Y:
            copied_name = prefix + self.name + suffix
        elif self.name in exclusive:
            copied_name = prefix + self.name + suffix
        elif share and not self.share:
            copied_name = prefix + self.name + suffix
        elif (not share) and (exclusive == []):
            copied_name = prefix + self.name + suffix
        else:
            copied_name = self.name

        copied_var = Variable(
            name=copied_name,
            value=self.value,
            type=self.type,
            bounds=self.bounds,
            term=self.term,
            share=self.share,
        )
        return copied_var


# from collections import deque
# from typing import Dict, Optional, Tuple

# import sympy
# from aphreco.enums import ItemType

# from .base import BaseComponent


# class Var(BaseComponent):
#     def __init__(
#         self,
#         name: str,
#         vtype: str = "y",
#         value: float = 0.0,
#         term: Optional[str] = None,
#         bounds: Optional[Tuple[float, float]] = None,
#     ):
#         self.name = name
#         self.type = vtype

#         self.value = float(value)

#         if bounds is None:
#             self.bounds = None
#         else:
#             self.bounds = (float(bounds[0]), float(bounds[1]))

#         if term is None:
#             self.term = None
#         else:
#             if self.type != ItemType.Y:
#                 raise ValueError(
#                     f"variable type must be 'y' when cre term is used: {self.type}"
#                 )
#             self.term = term

#     @property
#     def type(self):
#         return self._type

#     @type.setter
#     def type(self, vtype: str):
#         if vtype not in VTYPES.keys():
#             raise ValueError(
#                 f"invalid variable type: {vtype} \
#                 \nvtype must be chosen from {tuple(VTYPES.keys())}"
#             )
#         self._type = VTYPES[vtype]

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, name: str):
#         self._name = name

#     def _get_symbols(self):
#         return sympy.sympify(self.name)

#     def _print_tree(self, indent=""):
#         print(f"{indent}{self}[{self.type.name}]")

#     def _remove_by_name(self, dq_path: deque):
#         pass

#     def _formulate(self, eq_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         if self.term is None:
#             return eq_dicts

#         dict_cre = eq_dicts["cre"]

#         if self.name not in dict_cre.keys():
#             dict_cre[self.name] = self.term
#         else:
#             raise ValueError(
#                 f"multiple CREs was found for a single variable '{self.name}'."
#             )

#         eq_dicts["cre"] = dict_cre
#         return eq_dicts

#     def _collect_values(self, val_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         if self.type == ItemType.Y:
#             dict_y = val_dicts["y"]
#             if self.name in dict_y.keys():
#                 raise ValueError(f"name duplication: {self.name}")
#             dict_y[self.name] = self.value
#             val_dicts["y"] = dict_y

#         elif self.type in (ItemType.P | ItemType.X):
#             dict_p = val_dicts["p"]
#             if self.name in dict_p.keys():
#                 raise ValueError(f"name duplication: {self.name}")
#             dict_p[self.name] = self.value
#             val_dicts["p"] = dict_p

#         if self.type == ItemType.X:
#             dict_x = val_dicts["x"]
#             if self.name in dict_x.keys():
#                 raise ValueError(f"name duplication: {self.name}")
#             dict_x[self.name] = (self.value, self.bounds)
#             val_dicts["x"] = dict_x

#         return val_dicts


# class Y(BaseComponent):
#     def __new__(
#         cls,
#         name: str,
#         value: float = 0.0,
#         term: Optional[str] = None,
#     ):
#         return Var(name=name, value=value, vtype="y", term=term)


# class P(BaseComponent):
#     def __new__(
#         cls,
#         name: str,
#         value: float = 0.0,
#     ):
#         return Var(name=name, value=value, vtype="p", term=None)


# class X(BaseComponent):
#     def __new__(
#         cls,
#         name: str,
#         value: float = 0.0,
#         bounds: Optional[Tuple[float, float]] = None,
#     ):
#         return Var(name=name, value=value, vtype="x", term=None, bounds=bounds)


# class Beat:
#     def __new__(
#         cls,
#         name: Tuple[str, str, str],
#         value: Tuple[float, float, float],
#     ):
#         if isinstance(name, (list, tuple)):
#             name_start = name[0]
#             name_stop = name[1]
#             name_interval = name[2]
#         else:
#             raise ValueError(
#                 f"name must be string or tuple/list of three string objects."
#             )

#         if isinstance(value, (list, tuple)):
#             value_start = value[0]
#             value_stop = value[1]
#             value_interval = value[2]

#         beat = [
#             Var(name=name_start, value=value_start, vtype="p"),
#             Var(name=name_stop, value=value_stop, vtype="p"),
#             Var(name=name_interval, value=value_interval, vtype="p"),
#         ]
#         return beat
