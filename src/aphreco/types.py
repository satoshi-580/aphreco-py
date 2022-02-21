from typing import Any, Dict, List, Optional, Tuple, Union

from aphreco.enums import ItemType

# {yp_name: (itemtype, yp_index)}
NamesDict = Dict[str, Tuple[ItemType, int]]

# {yp_name: value}
ValsDict = Dict[str, float]

# {
#   "ode": {yname: rhs}
#   "rec": {(start, stop, step): rhs or {cond: (rhs of truecase, rhs of falsecase)}}
#   "cre": {yname: rhs}
# }
TermsDict = Dict[str, Dict[Any, Union[str, Dict[str, Tuple[str, str]]]]]

# {x_name: (x0, p_index, (lb, ub))}
UnksDict = Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]]

# [(y_name, t, y, terr, yerr, y_index)]
Table = List[Tuple[str, float, float, Optional[float], Optional[float], int]]
