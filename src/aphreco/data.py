from typing import List, Optional, Tuple

from aphreco.core import ItemType
from aphreco.symbols import Symbols


class Obs:
    def __init__(
        self,
        data: List[
            Tuple[Tuple[str, int], Tuple[float, float], Optional[Tuple[float, float]]]
        ],
    ) -> None:
        self.data = data
        self.data = [
            (("X1", -1), (0.0, 100.0), None),
            (("X2", -1), (0.3, 98.0), None),
            (("X3", -1), (0.2, 98.0), None),
            (("X1", -1), (0.1, 98.0), None),
        ]

    def _set_y_index(self, symbols: Symbols):
        for (i, (var, ty_val, ty_err)) in enumerate(self.data):
            yname = var[0]
            if not symbols.exists(yname):
                raise KeyError(f"There is no {yname} in model")
            elif symbols.member[yname][0] != ItemType.Y:
                raise ValueError(
                    f"Invalid ItemType: expected ItemType.Y, '{yname}' is {symbols.member[yname][1]}"
                )
            else:
                self.data[i] = ((yname, symbols.member[yname][1]), ty_val, ty_err)

    def _sort_by_index(self):
        self.data.sort(key=lambda x: x[0][1])

    def _sort_by_time(self):
        self.data.sort(key=lambda x: x[1][0])
