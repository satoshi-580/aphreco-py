from collections import OrderedDict
from typing import Dict

from aphreco.enums import ItemType
from aphreco.symbols import Symbols

from .source import ReplacedSource, Source


class Replacer:
    @classmethod
    def run(cls, source: Source, symbols: Symbols):
        repmap = cls.create_repmap(symbols)
        rep_source = cls.replace_symbols(source, repmap)
        return rep_source

    @classmethod
    def create_repmap(cls, symbols: Symbols):
        """create a map for replacement
        symbol name: replaced string y[index] or p[index]
        """
        sorted_member = OrderedDict(
            sorted(symbols.member.items(), key=lambda k: len(k[0]), reverse=True)
        )

        repmap = OrderedDict()
        for name, (vtype, index) in sorted_member.items():
            if vtype == ItemType.Y:
                repmap[name] = "y[" + str(index) + "]"
            if vtype in (ItemType.P | ItemType.X):
                repmap[name] = "self.p[" + str(index) + "]"

        return repmap

    @classmethod
    def replace_symbols(cls, source: Source, repmap: Dict[str, str]):
        """replace symbols by y[i] or self.p[i]"""
        rep_source = ReplacedSource()
        rep_source.lines = source.lines

        for name, code in repmap.items():
            rep_source.lines["ode"] = source.lines["ode"].replace(name, code)
            rep_source.lines["rec"] = source.lines["rec"].replace(name, code)
            rep_source.lines["beat"] = source.lines["beat"].replace(name, code)
            rep_source.lines["cre"] = source.lines["cre"].replace(name, code)

        return rep_source
