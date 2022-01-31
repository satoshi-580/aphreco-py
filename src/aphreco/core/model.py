import itertools
from collections import OrderedDict
from typing import Dict, List, Optional, Set, Tuple

from aphreco.core.base import BaseItem
from aphreco.enums import ItemType
from aphreco.errors import NameDuplicationError


class Model(BaseItem):
    """Model represents a composite of items in a model tree.

    A Model object can contain objects of Variable, Edge, and Model itself.
    The items are included in self.items, so that a client can visit them recursively.

    Attributes:
        name (str): The name of model

        items (OrderedDict): a dictionary that contains
            children's name and objects

        type (ItemType): class member, ItemType.MODEL

        hide (bool): whether or not print children
            when printing the model structure

    Example:
        >>> import aphreco as ap
        >>> model = ap.Model("sample")
        >>> model.name
        sample
    """

    type = ItemType.MODEL

    def __init__(self, name="", items: Dict[str, BaseItem] = None, hide=False):
        self.name = name
        items = items
        self.items: Dict[str, BaseItem] = OrderedDict()
        self.hide = hide

    def __iter__(self):
        return iter(self.items.items())

    def add(self, new_items, duplicate: str = "error"):
        if not isinstance(new_items, list):
            new_items = [new_items]

        if duplicate != ("error" or "skip"):
            raise ValueError(f"invalid argument: {duplicate}")
        if duplicate == "error":
            has_checked_dup = self.check_duplication(new_items)
            # has_checked_dup is always True in this case.
        else:
            has_checked_dup = False
            # if has_checked_dup is False and a duplication is found,
            # it means that adding the Variable should be skipped.

        new_model = self._add(new_items, has_checked_dup)
        for name, item in new_model.items():
            self.items[name] = item

    def _add(self, new_items, has_checked_dup, model=None):
        if model is None:
            model = Model()

        for new_item in new_items:
            if not isinstance(new_item, BaseItem):
                raise TypeError(f"invalid type: {type(new_item)}")

            elif isinstance(new_item, Model):
                self.items[new_item.name] = new_item

        return model

    def check_duplication(self, new_items) -> bool:
        """checks if the new_items have the name that has already existed.

        Args:
            new_items: List[Any of BaseItem]

        Returns:
            bool: This method always returns True because the process raises Error
                if the arg 'new_items' does not pass the check.
                The bool indicates if the new_items has passed the check or not.

        """
        # 1) check duplication of names inside new_items
        # collect new_names from new_items
        new_names_dict_list = list()
        for new_item in new_items:
            new_names_dict = new_item.collect_names(OrderedDict())
            new_names_dict_list.append(new_names_dict)

        # In the case of length of new_items >= 2, name duplications for all combinations of
        # list components will be checked.
        # if length of new_items is 1, the process does not reach inside this for-loop.
        for a, b in itertools.combinations(new_names_dict_list, 2):
            intersection = a.keys() & b.keys()
            if intersection != set():
                raise NameDuplicationError(intersection)

        # 2) check duplication between new_items and items in the original model.
        union: Set[str] = set()
        for new in new_names_dict_list:
            union = union | new.keys()

        names_dict = self.collect_names(OrderedDict())
        intersection = union & names_dict.keys()
        if intersection != set():
            raise NameDuplicationError(intersection)

        return True

    def collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        """recursively collects all names of Y, P, X, E below the current model.

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
        if len(self.items) == 0:
            return names_dict

        for item in self:
            names_dict = item.collect_names(names_dict)
        return names_dict

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        """creates a str list of tree components."""
        if structure is None:
            structure = list()

        if not self.hide:
            structure.append(f"{indent}{self.name}/")
            for _, item in self:
                structure = item.tree(indent + "  ", structure)
        else:
            structure.append(f"{indent}{self.name}/...")

        return structure

    def copy(self, prefix="", suffix="", exclusive=[], share=True):
        model = Model(self.name)
        for item in self:
            model.add(item.copy(prefix, suffix, exclusive, share))
        return model


# from collections import OrderedDict, deque
# from typing import Dict, Optional

# from aphreco.enums import ItemType

# from .base import BaseComponent
# from .variable import Var


# class Model(BaseComponent):
#     def __init__(
#         self,
#         name: str,
#     ):
#         self.name = name
#         self.type = mtype
#         self.items: Dict[str, BaseItem] = OrderedDict()

#     def __iter__(self):
#         return iter(self.items.items())

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, name: str):
#         self._name = name

#     @property
#     def type(self):
#         return self._type

#     @type.setter
#     def type(self, mtype: str):
#         if mtype not in MTYPES.keys():
#             raise ValueError(
#                 f"invalid model type: {mtype} \
#                 \nmtype must be chosen from {tuple(MTYPES.keys())}"
#             )
#         self._type = MTYPES[mtype]

#     def _print_tree(self, indent=""):
#         if self.type == ItemType.BOX:
#             print(f"{indent}{self}/")
#             for _, item in self:
#                 item._print_tree(indent + "  ")
#         elif self.type == ItemType.BLACKBOX:
#             print(f"{indent}{self}/...")

#     def _get_item(self, dq_path: deque) -> Optional[BaseItem]:
#         name = dq_path.popleft()
#         if name not in self.items.keys():
#             return None
#         elif len(dq_path) == 0:
#             return self.items[name]
#         else:
#             next_item = self.items[name]
#             if isinstance(next_item, (Var, BaseEdge)):
#                 raise ValueError(f"item '{name}' is a component, not a model")
#             elif isinstance(next_item, BaseModel):
#                 return next_item._get_item(dq_path)
#             else:
#                 return None

#     def _add(self, item: BaseItem, symbols: Optional[Symbols] = None):
#         if symbols is None:
#             self.items[item.name] = item
#         else:
#             print(str(item), symbols.exists(str(item)))

#     def _find_name(self, name, path: str) -> Optional[str]:
#         ans = None
#         for key, item in self:
#             if key == name:
#                 ans = f"{path}{self._name}/"
#                 break
#             elif isinstance(item, BaseModel):
#                 ans = item._find_name(name, f"{path}{self._name}/")
#                 if ans is not None:
#                     break
#         return ans

#     def _formulate(self, eq_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         """Collect terms of Edge objects or cre in Y objects by Depth-First Search.
#         eq_dicts: Dict['ode': dict_ode, 'rec': dict_rec, 'cre': dict_cre]
#             dict_ode: Dict[lhs, rhs]
#             dict_rec: Dict[(start, stop, step): Dict[lhs, rhs]]
#             dict_cre: Dict[lhs, rhs]
#         """
#         for _, item in self:
#             if isinstance(item, BaseModel):
#                 eq_dicts = item._formulate(eq_dicts)
#             elif isinstance(item, Var):
#                 eq_dicts = item._formulate(eq_dicts)
#             elif isinstance(item, BaseEdge):
#                 eq_dicts = item._formulate(eq_dicts)
#         return eq_dicts

#     def _collect_values(self, val_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         """Collect values of Var objects in a model by Depth-First Search.
#         val_dicts: Dict['y': dict_y, 'p': dict_p, 'x': dict_x]
#             dict_y: Dict[name, y0 (initial state value)]
#             dict_p: Dict[name, p (constant value)]
#             dict_x: Dict[name, (value, bounds)]
#         """
#         for _, item in self:
#             if isinstance(item, BaseModel):
#                 val_dicts = item._collect_values(val_dicts)
#             elif isinstance(item, Var):
#                 val_dicts = item._collect_values(val_dicts)
#             elif isinstance(item, BaseEdge):
#                 continue
#         return val_dicts
