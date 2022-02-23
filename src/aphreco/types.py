from typing import Dict, List, Optional, Tuple, Union

from aphreco.enums import ItemType

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
#   {(start, stop, step): [rhs or {cond: (rhs of truecase, rhs of falsecase)}]},
#   {yname: [rhs]},
# )
OdeTerms = Dict[str, List[str]]
RecTerms = Dict[str, List[Union[str, Ternary]]]
CreTerms = Dict[str, List[Union[str, Ternary]]]
TermsDicts = Tuple[OdeTerms, Dict[Beat, RecTerms], CreTerms]

# {x_name: (x0, p_index, (lb, ub))}
UnksDict = Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]]

# [(y_name, t, y, terr, yerr, y_index)]
Table = List[Tuple[str, float, float, Optional[float], Optional[float], int]]
