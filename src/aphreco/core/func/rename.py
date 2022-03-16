import re
from typing import List, Tuple


def rename_all(term: str, old: str, new: str):
    positions = _find_all_with_isidentifier_check(term, old)
    renamed_term = _replace_all_by_positions(term, new, positions)
    return renamed_term


def _find_all_with_isidentifier_check(term: str, old: str) -> List[Tuple[int, int]]:
    # positions have tuples of (start, end)
    positions = list()

    for m in re.finditer(old, term):
        s = m.start()
        e = m.end()

        # check prefix
        # catch variable without prefix or suffix
        if not term[s - 1 : e].isidentifier():
            # check suffix
            if e == len(term) or not term[s : e + 1].isidentifier():
                positions.append((s, e))

        # also catch delta_ and deriv_
        elif (term[s - 6 : s] == "delta_" or term[s - 6 : s] == "deriv_") and (
            not term[s - 7 : s].isidentifier()
        ):
            if e == len(term) or not term[s : e + 1].isidentifier():
                positions.append((s, e))

    return positions


def _replace_all_by_positions(
    term: str,
    new: str,
    positions: List[Tuple[int, int]],
) -> str:

    # create a indices list with (start, end) for new.join()
    pos_list = list()
    pos = 0
    for s, e in positions:
        pos_list.append((pos, s))
        pos = e
    pos_list.append((pos, len(term)))

    if len(pos_list) == 1:
        return term

    return new.join([term[s:e] for s, e in pos_list])


def create_name_from_term(term, prefix, relation):
    str_from = ""
    str_to = ""
    for name, term in term.items():
        if isinstance(term, tuple):
            cond = term[0]
            true = term[1]
            false = term[2]
            str_term = f"{prefix}{name}{relation}if {cond} {{{true}}} else {{{false}}},"
            starts_with_minus = true.lstrip()[0] == "-"

        elif isinstance(term, str):
            str_term = f"{prefix}{name}{relation}{term},"
            starts_with_minus = term.lstrip()[0] == "-"

        if starts_with_minus:
            str_from += str_term
        else:
            str_to += str_term

    name = f"{str_from[:-1]} -> {str_to[:-1]}"
    name = name.strip()
    return name
