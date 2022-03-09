from typing import Dict, List, Optional, Tuple, Union

from aphreco.enums import ItemType


class Inline:
    @property
    def code(self):
        return self._code

    @code.setter
    def code(self, code):
        self._code = code

    def __init__(self, code):
        self.code = code


# {yp_name: (itemtype, yp_index)}
NamesDict = Dict[str, Tuple[ItemType, int]]

# {yp_name: value}
ValsDict = Dict[str, float]

# definition
Ternary = Tuple[str, str, str]
Beat = Tuple[str, str, str]
OdeTerm = Dict[str, Union[str, Ternary]]
RecTerm = Dict[str, Union[str, Ternary]]
CreTerm = Union[str, Ternary]

# In collecting, ...
# (
#   {yname: [rhs]},
#   {(start, stop, step): [rhs or (cond, true-rhs, false-rhs)]},
#   {yname: [rhs]},
# )
OdeTerms = Dict[str, List[Union[str, Ternary, Inline]]]
RecTerms = Dict[str, List[Union[str, Ternary, Inline]]]
CreTerms = Dict[str, Union[str, Ternary, Inline]]
TermsDicts = Tuple[OdeTerms, Dict[Beat, RecTerms], CreTerms]

# {x_name: (x0, p_index, (lb, ub))}
UnksDict = Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]]

# [(y_name, t, y, terr, yerr, y_index)]
Table = List[Tuple[str, float, float, Optional[float], Optional[float], int]]
