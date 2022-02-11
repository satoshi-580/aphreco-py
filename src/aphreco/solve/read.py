import csv
import glob
from pathlib import Path
from typing import List, Union


class SimResult:
    def __init__(self, t, y):
        self.t = t
        self.y = y
        self.log = ""
        self.nfev = {"ode": 0, "rec": 0, "cre": 0}


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
        if not isinstance(path_dir, Path):
            path_dir = Path(path_dir)

        if not no_pandas:
            # returns DataFrame
            gb_file = glob.glob(str(path_dir / "Sim_*.csv"))
            ty = pd.read_csv(gb_file[0], header=None)
            t = ty.iloc[:, 0]
            y = ty.iloc[:, 1:]
            if ynames is not None:
                y = y.set_axis(ynames, axis="columns")

        elif not no_numpy:
            # returns ndarray
            gb_file = glob.glob(str(path_dir / "Sim_*.csv"))
            ty = np.loadtxt(str(gb_file[0]), delimiter=",")
            t = ty[:, 0]
            y = ty[:, 1:]

        else:
            # returns list
            t = list()
            y = dict()
            for res_file in path_dir.glob("Sim_*.csv"):
                with res_file.open("r") as f:
                    csvreader = csv.reader(f)
                    for line in csvreader:
                        t.append(line[0])
                        for i, value in enumerate(line[1:]):
                            if ynames is not None:
                                key = ynames[i]
                            else:
                                key = i

                            if key not in y.keys():
                                y[key] = [value]
                            else:
                                y[key].append(value)

        simres = SimResult(t, y)
        return simres
