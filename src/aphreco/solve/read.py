import csv
import glob
from pathlib import Path
from typing import List, Union

no_pandas = False
try:
    import pandas as pd
except ImportError:
    no_pandas = True

no_numpy = False
try:
    import numpy as np
except ImportError:
    no_numpy = True


class SimResult:
    def __init__(self, t, y):
        self.t = t
        self.y = y
        self.log = ""
        self.nfev = {"ode": 0, "rec": 0, "cre": 0}


class ResReader:
    @property
    def fname(self):
        return self._fname

    @fname.setter
    def fname(self, fname):
        self._fname = fname


class SimResReader(ResReader):
    def __init__(self):
        pass

    def read(self, path_dir: Union[Path, str], ynames: List[str]):
        """reads a simulated result.

        The order of reading t and y of a simulated result is as follows;
        1) by pandas, reading t as a Series and y as a DataFrame
        2) by numpy, reading t as a 1d-array and y as a 2d-array
        3) as a list for t and a dict for y if neither pandas or numpy are available.

        If designate 'ynames', ynames are set to columns of the y DataFrame if pandas is available,
        or set to keys of the y dict if neither pandas nor numpy is installed.
        'ynames' is not used in the case of numpy.

        Args:
            path_dir Union[Path, str]: The directory path of the simulated result.
                Recommend not to rename a file 'Sim_***.csv' (*** is a datetime).

            ynames (List[str]): The list of names of dependent variables in a model.
                They can be obtained from 'Model.ynames'.
        """
        if not isinstance(path_dir, Path):
            path_dir = Path(path_dir)

        # to be passed to glob and read an only first file.
        csv_name = "result.csv"

        # read a file by pandas, numpy, or a standard way.
        if not no_pandas:
            # returns SimResult with a Series of t and a DataFrame of y.
            gb_file = glob.glob(str(path_dir / csv_name))
            ty = pd.read_csv(gb_file[0], header=None)
            t = ty.iloc[:, 0]
            y = ty.iloc[:, 1:]
            if ynames is not None:
                y = y.set_axis(ynames, axis="columns")

        elif not no_numpy:
            # returns SimResult with ndarray of t and y.
            gb_file = glob.glob(str(path_dir / csv_name))
            ty = np.loadtxt(str(gb_file[0]), delimiter=",")
            t = ty[:, 0]
            y = ty[:, 1:]

        else:
            # returns SimResult with a list of t and a dict of y.
            t = list()
            y = dict()
            gb_file = glob.glob(str(path_dir / csv_name))
            with open(str(gb_file[0]), "r") as f:
                csvreader = csv.reader(f)
                for line in csvreader:
                    t.append(float(line[0]))
                    for i, value in enumerate(line[1:]):
                        key = i if ynames is None else ynames[i]
                        if key not in y.keys():
                            y[key] = [float(value)]
                        else:
                            y[key].append(float(value))

        simres = SimResult(t, y)
        return simres
