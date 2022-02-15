import csv
import math
from pathlib import Path
from typing import Union

from aphreco.enums import ItemType
from aphreco.types import NamesDict, Table

no_pandas = False
try:
    import pandas as pd
except ImportError:
    no_pandas = True


class Data:
    def __init__(self, table: Table) -> None:
        self.table = table

    def _list_cells(self, target, name):
        target_index = {
            "name": 0,
            "t": 1,
            "y": 2,
            "terr": 3,
            "yerr": 4,
        }
        idx = target_index[target]
        if name is None:
            return [record[idx] for record in self.table]
        else:
            return [record[idx] for record in self.table if record[0] == name]

    def y(self, name=None):
        return self._list_cells("y", name)

    def t(self, name=None):
        return self._list_cells("t", name)

    def name(self, name=None):
        return self._list_cells("name", name)

    def terr(self, name=None):
        return self._list_cells("terr", name)

    def yerr(self, name=None):
        return self._list_cells("yerr", name)

    @classmethod
    def from_df(cls, df):
        # store df contents into a list 'table'.
        table = list()
        num_data = df.shape[0]
        num_cols = df.shape[1]

        names = df.iloc[:, 0].values
        ts = df.iloc[:, 1].values
        ys = df.iloc[:, 2].values

        if num_cols >= 4:
            terrs = df.iloc[:, 3].values
        else:
            terrs = [None] * num_data

        if num_cols >= 5:
            yerrs = df.iloc[:, 4].values
        else:
            yerrs = [None] * num_data

        for idx in range(num_data):
            terr = None if math.isnan(terrs[idx]) else terrs[idx]
            yerr = None if math.isnan(yerrs[idx]) else yerrs[idx]
            table.append((names[idx], ts[idx], ys[idx], terr, yerr, -1))

        data = Data(table)
        return data

    def set_yindex(self, names_dict: NamesDict):
        for i, (yname, t, y, terr, yerr, _) in enumerate(self.table):
            if yname not in names_dict.keys():
                raise KeyError(f"model has no '{yname}' as y.")

            if names_dict[yname][0] != ItemType.Y:
                raise KeyError(f"Variable '{yname}' is not ItemType.Y in a model.")

            idx = names_dict[yname][1]
            self.table[i] = (yname, t, y, terr, yerr, idx)

    def sort_by_index(self):
        self.table.sort(key=lambda x: x[5])

    def sort_by_time(self):
        self.table.sort(key=lambda x: x[1])


def _append_record(table, values):
    if len(values) == 3:
        # [name, t, y, terr=None, yerr=None, y_index=-1]
        table.append((values[0], float(values[1]), float(values[2]), None, None, -1))

    elif len(values) == 4:
        # [name, t, y, terr, yerr=None, y_index=-1]
        terr = None if values[3] == "" else float(values[3])
        table.append((values[0], float(values[1]), float(values[2]), terr, None, -1))

    elif len(values) >= 5:
        # [name, t, y, terr, yerr, y_index=-1]
        terr = None if values[3] == "" else float(values[3])
        yerr = None if values[4] == "" else float(values[4])
        table.append(
            (str(values[0]), float(values[1]), float(values[2]), terr, yerr, -1)
        )

    else:
        raise ValueError("not formatted data in csv")


def read_data(csvpath: Union[Path, str], header=None) -> Data:
    """reads observation data from a csv file.

    The order of reading is as follows;
    1) try by pandas, reading data as a DataFrame
    3) try as a tuple for t and a dict for y if neither pandas or numpy are available.

    Args:
        csvpath Union[Path, str]: The file path of observation data csv.
            The csv file should contains data with a format of [yname, t, y, (terr), (yerr)]
    """
    if not isinstance(csvpath, Path):
        csvpath = Path(csvpath)

    # read a file by pandas or a standard way.
    if not no_pandas:
        df_table = pd.read_csv(csvpath, header=header)
        return Data.from_df(df_table)

    else:
        table: Table = list()
        with open(csvpath, "r") as f:
            csvreader = csv.reader(f)
            for values in csvreader:
                table = _append_record(table, values)
        return Data(table)


# class Data:
#     def __init__(self) -> None:
#         self.data: Optional[
#             List[Tuple[str, float, float, Optional[float], Optional[float], int]]
#         ] = None

#     def read_obs(self, csv_path):
#         with open(csv_path) as f:
#             reader = csv.reader(f)
#             data = [
#                 (
#                     row[0],
#                     float(row[1]),
#                     float(row[2]),
#                     None if len(row) <= 3 else {float(row[3])},
#                     None if len(row) <= 4 else {float(row[4])},
#                     -1,
#                 )
#                 for row in reader
#             ]
#         self.data = data

#     def set_y_index(self, symbols: Symbols):
#         if self.data is None:
#             raise ValueError("No data found.")

#         if not isinstance(self.data, list):
#             raise TypeError("invalid data type")

#         for (i, (symbol, t, y, t_err, y_err, _)) in enumerate(self.data):
#             if not symbols.exists(symbol):
#                 # cannot define data for a non-registered symbol
#                 raise KeyError(f"variable '{symbol}' not found")

#             elif symbols.member[symbol][0] != ItemType.Y:
#                 # data must be referred by a dependent variable y.
#                 raise ValueError(
#                     f"invalid ItemType: '{symbol}'. found {symbols.member[symbol][1]}, expected ItemType.Y."
#                 )

#             elif symbols.member[symbol][1] == -1:
#                 # -1 is initialized value for yp-index
#                 raise ValueError(f"index in Symbols.member has not been set yet.")

#             else:
#                 self.data[i] = (symbol, t, y, t_err, y_err, symbols.member[symbol][1])

#     def sort_by_index(self):
#         self.data.sort(key=lambda x: x[5])

#     def sort_by_time(self):
#         self.data.sort(key=lambda x: x[1])
