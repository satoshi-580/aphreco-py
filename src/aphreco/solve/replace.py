from collections import OrderedDict
from typing import Dict, Tuple

from aphreco.enums import ItemType


class Replacer:
    def __init__(self):
        pass

    def create_repmap(cls, names_dict: Dict[str, Tuple[ItemType, int]]):
        """create a map for replacement
        symbol name: replaced string y[index] or p[index]
        """
        sorted_names = OrderedDict(
            sorted(names_dict.items(), key=lambda k: len(k[0]), reverse=True)
        )

        repmap = OrderedDict()
        for name, (vartype, index) in sorted_names.items():
            if vartype == ItemType.Y:
                repmap[name] = "y[" + str(index) + "]"
            if vartype in (ItemType.P | ItemType.X | ItemType.I):
                repmap[name] = "self.p[" + str(index) + "]"

        return repmap

    def replace_names_in_terms(self, lines: Dict[str, str], repmap: Dict[str, str]):
        """replace names by y[i] or self.p[i]"""
        rep_lines = lines.copy()

        for name, code in repmap.items():
            rep_lines["ode"] = rep_lines["ode"].replace(name, code)
            rep_lines["rec"] = rep_lines["rec"].replace(name, code)
            rep_lines["beat"] = rep_lines["beat"].replace(name, code)
            rep_lines["cre"] = rep_lines["cre"].replace(name, code)

        return rep_lines
