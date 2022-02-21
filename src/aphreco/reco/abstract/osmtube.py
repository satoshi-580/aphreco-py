from typing import Dict, List, Tuple

from aphreco.core import Reg
from aphreco.enums import ItemType


class OsmExtrusion(Reg):
    def __init__(
        self,
        beat: Tuple[str, str, str],
        term: Dict[str, str],
        name: str = None,
        prelines: List[str] = None,
        prolines: List[str] = None,
        _is_default_name: bool = None,
    ):
        super().__init__(beat, term, name, _is_default_name)

        if prelines is not None:
            self.prelines = prelines

        if prolines is not None:
            self.prolines = prolines
