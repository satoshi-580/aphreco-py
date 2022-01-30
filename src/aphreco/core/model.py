from collections import OrderedDict

from aphreco.core.base import BaseItem
from aphreco.enums import ItemType


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

    def __init__(self, name="", items=None, hide=False):
        self.name = name
        items = items
        self.items = OrderedDict()
        self.hide = hide

    def __iter__(self):
        return iter(self.items.items())

    def _print(self, indent: str):
        if self.hide:
            print(f"{indent}{self.name}/...")
        else:
            print(f"{indent}{self.name}/")
            for _, item in self:
                item._print(indent + "  ")

    def add(self, items, duplicate="error"):
        if duplicate == "skip":
            print("function does not check the duplication of name")

    def _collect_names(self, result):
        raise NotImplementedError


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
