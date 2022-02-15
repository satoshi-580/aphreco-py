from typing import Any, Dict, List, Optional, Tuple

from aphreco.enums import ItemType

Table = List[Tuple[str, float, float, Optional[float], Optional[float], int]]
NamesDict = Dict[str, Tuple[ItemType, int]]
ValsDict = Dict[str, float]
TermsDict = Dict[str, Dict[Any, str]]
UnksDict = Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]]
