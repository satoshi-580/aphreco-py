from collections import OrderedDict
from typing import Dict, Tuple

from aphreco.core import ItemType


class Symbols:
    def __init__(self) -> None:
        self.member: Dict[str, Tuple[ItemType, int]] = OrderedDict()

    def keys(self):
        return self.member.keys()

    def exists(self, symbol: str) -> bool:
        return symbol in self.member.keys()

    def add(self, new_symbol: str, vtype: ItemType, index: int = -1):
        """add a new symbol to Symbols.registered. (default index is 0)"""
        if self.exists(new_symbol):
            raise ValueError(f"There has already been {new_symbol} in a model.")

        if vtype not in ItemType.VARIABLE:
            raise ValueError(f"expected {ItemType.VARIABLE}, but found {vtype}")

        self.member[new_symbol] = (vtype, index)

    def set_index(self, name: str, index: int):
        """update a index of which the sybmol has already been registered."""
        if not self.exists(name):
            raise ValueError(f"{name} not found.")

        (vtype, _) = self.member[name]
        self.member[name] = (vtype, index)
