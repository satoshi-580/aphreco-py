from typing import Set

import sympy


def extract_symset(term: str) -> Set[str]:
    symbols_set = sympy.sympify(term).atoms(sympy.Symbol)
    str_symbols_set = {str(symbol) for symbol in symbols_set}
    return str_symbols_set


def str_symbol_name(name: str) -> str:
    if not name.isidentifier():
        raise ValueError(f"invalid name for identifier: '{name}'")

    return str(sympy.sympify(name))
