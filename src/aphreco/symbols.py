from collections import OrderedDict
from typing import Dict, Tuple

from aphreco.core import ItemType


class Symbols:
    def __init__(self) -> None:
        self.registered: Dict[str, Tuple[ItemType, int]] = OrderedDict()

    def exists(self, symbol: str) -> bool:
        return symbol in self.registered.keys()

    def add(self, new_symbol: str, vtype: ItemType, index: int = 0):
        """add a new symbol to Symbols.registered. (default index is 0)"""
        if self.exists(new_symbol):
            raise ValueError(f"There has already been {new_symbol} in a model.")

        self.registered[new_symbol] = (vtype, index)

    def set_index(self, symbol: str, index: int):
        """update a index of which the sybmol has already been registered."""
        if not self.exists(symbol):
            raise ValueError(f"{symbol} not found.")

        (vtype, _) = self.registered[symbol]
        self.registered[symbol] = (vtype, index)
