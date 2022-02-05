import re
from typing import List, Tuple


def rename_all(term: str, old: str, new: str):
    positions = _find_all_with_isidentifier_check(term, old)
    renamed_term = _replace_all_by_positions(term, new, positions)
    return renamed_term


def _find_all_with_isidentifier_check(term: str, old: str) -> List[Tuple[int, int]]:
    positions = list()
    for m in re.finditer(old, term):
        s = m.start()
        e = m.end()
        # check prefix
        if not term[s - 1 : e].isidentifier():
            # check suffix
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
