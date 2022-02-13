import csv
from pathlib import Path
from typing import Union

no_pandas = False
try:
    import pandas as pd
except ImportError:
    no_pandas = True


def read_data(csvpath: Union[Path, str], header=None):
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
        # returns data as a DataFrame.
        data = pd.read_csv(csvpath, header=header)

    else:
        # returns data as a list of tuples (yname:str, t:float, y:float, terr:float, yerr:float).
        data = list()
        with open(csvpath, "r") as f:
            csvreader = csv.reader(f)
            for line in csvreader:
                if len(line) == 3:
                    # [name, t, y, terr=None, yerr=None]
                    data.append(
                        (
                            line[0],
                            float(line[1]),
                            float(line[2]),
                            None,
                            None,
                        )
                    )

                elif len(line) == 4:
                    # [name, t, y, terr, yerr=None]
                    terr = None if line[3] == "" else float(line[3])
                    data.append(
                        (
                            line[0],
                            float(line[1]),
                            float(line[2]),
                            float(line[3]),
                            None,
                        )
                    )

                elif len(line) >= 5:
                    # [name, t, y, terr, yerr]
                    terr = None if line[3] == "" else float(line[3])
                    yerr = None if line[4] == "" else float(line[4])
                    data.append(
                        (
                            str(line[0]),
                            float(line[1]),
                            float(line[2]),
                            float(line[3]),
                            float(line[4]),
                        )
                    )

                else:
                    raise ValueError("not formatted data in csv")

    return data
