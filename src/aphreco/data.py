import csv
from typing import List, Optional, Tuple

from aphreco.core import ItemType
from aphreco.symbols import Symbols


class Obs:
    def __init__(self) -> None:
        self.data: Optional[
            List[Tuple[str, float, float, Optional[float], Optional[float], int]]
        ] = None

    def read_obs(self, csv_path):
        with open(csv_path) as f:
            reader = csv.reader(f)
            data = [
                (
                    row[0],
                    float(row[1]),
                    float(row[2]),
                    None if len(row) <= 3 else {float(row[3])},
                    None if len(row) <= 4 else {float(row[4])},
                    -1,
                )
                for row in reader
            ]
        self.data = data

    def set_y_index(self, symbols: Symbols):
        if self.data is None:
            raise ValueError("No data found.")

        if not isinstance(self.data, list):
            raise TypeError("invalid data type")

        for (i, (symbol, t, y, t_err, y_err, _)) in enumerate(self.data):
            if not symbols.exists(symbol):
                # cannot define data for a non-registered symbol
                raise KeyError(f"variable '{symbol}' not found")

            elif symbols.member[symbol][0] != ItemType.Y:
                # data must be referred by a dependent variable y.
                raise ValueError(
                    f"invalid ItemType: '{symbol}'. found {symbols.member[symbol][1]}, expected ItemType.Y."
                )

            elif symbols.member[symbol][1] == -1:
                # -1 is initialized value for yp-index
                raise ValueError(f"index in Symbols.member has not been set yet.")

            else:
                self.data[i] = (symbol, t, y, t_err, y_err, symbols.member[symbol][1])

    def sort_by_index(self):
        self.data.sort(key=lambda x: x[5])

    def sort_by_time(self):
        self.data.sort(key=lambda x: x[1])
