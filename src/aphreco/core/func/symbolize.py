import re
from typing import Set, Union

import sympy
from aphreco.types import Ternary


def _get_atoms(term):
    return sympy.sympify(term).atoms(sympy.Symbol)


PATTERN = re.compile(r"==|!=|>=|<=|<|>|&&|\|")


def _symset_in_condition(cond: str) -> Set[str]:
    cond_parts = PATTERN.split(cond)
    symset: Set[str] = set()
    for part in cond_parts:
        symset = symset | _get_atoms(part)
    return symset


def extract_symset(term: Union[str, Ternary]) -> Set[str]:
    if isinstance(term, str):
        symbols_set = _get_atoms(term)
        str_symbols_set = {str(symbol) for symbol in symbols_set}

    elif isinstance(term, tuple):
        symbols_cond = _symset_in_condition(term[0])
        symbols_true = _get_atoms(term[1])
        symbols_false = _get_atoms(term[2])
        symbols_set = symbols_cond | symbols_true | symbols_false
        str_symbols_set = {str(symbol) for symbol in symbols_set}

    return str_symbols_set


def str_symbol_name(name: str) -> str:
    if not name.isidentifier():
        raise ValueError(f"invalid name for identifier: '{name}'")

    return str(sympy.sympify(name))
