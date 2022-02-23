from typing import List, Set, Union

import sympy
from aphreco.types import Ternary


def extract_symset(term: Union[str, Ternary]) -> Set[str]:
    if isinstance(term, str):
        symbols_set = sympy.sympify(term).atoms(sympy.Symbol)
        str_symbols_set = {str(symbol) for symbol in symbols_set}

    elif isinstance(term, tuple):
        # symbols_cond = _symbolize_condition(term[0])
        symbols_true = sympy.sympify(term[1]).atoms(sympy.Symbol)
        symbols_false = sympy.sympify(term[2]).atoms(sympy.Symbol)
        symbols_set = symbols_true | symbols_false
        # symbols_set = symbols_cond | symbols_true | symbols_false
        str_symbols_set = {str(symbol) for symbol in symbols_set}

    return str_symbols_set


CMP_SIGNS = ["==", "!=", ">", "<", ">=", "<=", " and ", " or ", "|", "&&"]


def _symbolize_condition(cond: str) -> Set[str]:
    def _split_by_sign(cmp: str, ans=None):
        for sign in CMP_SIGNS:
            pass

    return set(["a", "b"])


def str_symbol_name(name: str) -> str:
    if not name.isidentifier():
        raise ValueError(f"invalid name for identifier: '{name}'")

    return str(sympy.sympify(name))
