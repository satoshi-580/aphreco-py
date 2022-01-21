from __future__ import annotations

from collections import OrderedDict, deque
from operator import eq
from typing import Dict, List, Optional, Union

from aphreco.types import ItemType

from .base import BaseEdge, BaseItem, BaseModel
from .variable import Var

MTYPES = {
    "box": ItemType.BOX,
    "blackbox": ItemType.BLACKBOX,
}


class Box(BaseModel):
    def __init__(
        self,
        name: str,
        mtype: str = "box",
    ):
        self.name = name
        self.type = mtype
        self.items: Dict[str, BaseItem] = OrderedDict()

    def __str__(self):
        return f"{self.name}[{self.type.name}]"

    def __iter__(self):
        return iter(self.items.items())

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, mtype: str):
        if mtype not in MTYPES.keys():
            raise ValueError(
                f"invalid model type: {mtype} \
                \nmtype must be chosen from {tuple(MTYPES.keys())}"
            )
        self._type = MTYPES[mtype]

    def _print_tree(self, indent=""):
        print(f"{indent}{self}/")
        if self.type != ItemType.BLACKBOX:
            for _, item in self:
                item._print_tree(indent + "  ")

    def _get_item(self, dq_path: deque) -> Optional[BaseItem]:
        name = dq_path.popleft()
        if name not in self.items.keys():
            return None
        elif len(dq_path) == 0:
            return self.items[name]
        else:
            next_item = self.items[name]
            if isinstance(next_item, (Var, BaseEdge)):
                raise ValueError(f"item '{name}' is a component, not a model")
            elif isinstance(next_item, BaseModel):
                return next_item._get_item(dq_path)
            else:
                return None

    def _add(self, item):
        self.items[item.name] = item

    def _find_name(self, name, path: str) -> Optional[str]:
        ans = None
        for key, item in self:
            if key == name:
                ans = f"{path}{self._name}/"
                break
            elif isinstance(item, BaseModel):
                ans = item._find_name(name, f"{path}{self._name}/")
                if ans is not None:
                    break
        return ans

    def _formulate(self, eq_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
        """Collect terms of Edge objects or cre in Y objects by Depth-First Search.
        eq_dicts: Dict['ode': dict_ode, 'rec': dict_rec, 'cre': dict_cre]
            dict_ode: Dict[lhs, rhs]
            dict_rec: Dict[(start, stop, step): Dict[lhs, rhs]]
            dict_cre: Dict[lhs, rhs]
        """
        for _, item in self:
            if isinstance(item, BaseModel):
                eq_dicts = item._formulate(eq_dicts)
            elif isinstance(item, Var):
                eq_dicts = item._formulate(eq_dicts)
            elif isinstance(item, BaseEdge):
                eq_dicts = item._formulate(eq_dicts)
        return eq_dicts

    def _collect_values(self, val_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
        """Collect values of Var objects in a model by Depth-First Search.
        val_dicts: Dict['y': dict_y, 'p': dict_p, 'x': dict_x]
            dict_y: Dict[name, y0 (initial state value)]
            dict_p: Dict[name, p (constant value)]
            dict_x: Dict[name, x0 (initial value to be optimized)]
        """
        for _, item in self:
            if isinstance(item, BaseModel):
                val_dicts = item._collect_values(val_dicts)
            elif isinstance(item, Var):
                val_dicts = item._collect_values(val_dicts)
            elif isinstance(item, BaseEdge):
                continue
        return val_dicts
