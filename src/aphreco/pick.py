from collections import OrderedDict

import sympy

from aphreco.core import BaseModel
from aphreco.symbols import Symbols


class Picker:
    def __init__(self):
        self.t = ""
        self.y = ""
        self.p = ""
        self.ode = ""
        self.rec = ""
        self.cond = ""
        self.beat = ""
        self.cre = ""

    def collect_equations(self, model: BaseModel):
        # dict_ode: Dict[lhs('deriv_' not yet added), rhs]
        # dict_rec: Dict[(start, stop, step), Dict[lhs('delta_' not yet added), rhs]]
        # dict_cre: Dict[lhs, rhs]
        eq_dicts = model._formulate(
            OrderedDict(ode=OrderedDict(), rec=OrderedDict(), cre=OrderedDict())
        )
        dict_ode = eq_dicts["ode"]
        dict_rec = eq_dicts["rec"]
        dict_cre = eq_dicts["cre"]

        # assemble ode
        str_ode = ""
        for lhs, rhs in dict_ode.items():
            eq = "deriv_" + lhs + " = " + str(sympy.sympify(rhs))
            str_ode += eq + "\n"
        self.ode = str_ode[:-1]

        # assemble rec/cond
        str_rec = ""
        str_cond = ""
        str_beat = ""
        for i, (beat, rec) in enumerate(dict_rec.items()):
            # rec
            str_rec += f"=== {i}: {beat}\n"
            for lhs, rhs in rec.items():
                eq = "delta_" + lhs + " += " + str(sympy.sympify(rhs))
                str_rec += eq + "\n"
            # cond
            str_cond += (
                f"  act[{i}] = if *dec_t == nect_t[{i}] {{ true }} else {{ false }};"
            )
            # beat
            str_beat += "beat![" + beat[0] + ", " + beat[1] + ", " + beat[2] + "],\n"
        self.rec = str_rec[:-1]
        self.cond = str_cond[:-1]
        self.beat = str_beat[:-1]

        # assemble cre
        str_cre = ""
        for lhs, rhs in dict_cre.items():
            eq = lhs + " = " + str(sympy.sympify(rhs))
            str_cre += eq + "\n"
        self.cre = str_cre[:-1]

    def collect_values(self, model, symbols: Symbols):
        val_dicts = model._collect_values(
            OrderedDict(y=OrderedDict(), p=OrderedDict(), x=OrderedDict())
        )
        dict_y = val_dicts["y"]
        dict_p = val_dicts["p"]  # This p contains both P and X variables
        dict_x = val_dicts["x"]

        # assemble y
        str_ini_y_with_replacement = ""
        max_vallen = 0
        for i, (name, value) in enumerate(dict_y.items()):
            symbols.set_index(name, i)
            # '//' is a comment format in Rust lang.
            str_ini_y_with_replacement += f"{value},***space***// y[{i}] {name}\n"
            vallen = len(str(value))
            max_vallen = vallen if max_vallen < vallen else max_vallen
        str_ini_y = ""

        for line in str_ini_y_with_replacement.splitlines():
            vallen = line.find(",")
            num_space = max_vallen - vallen + 1
            str_ini_y += line.replace("***space***", " " * num_space) + "\n"

        # assemble p
        str_p_with_replacement = ""
        max_vallen = 0
        for i, (name, value) in enumerate(dict_p.items()):
            symbols.set_index(name, i)
            # '//' is a comment format in Rust lang.
            str_p_with_replacement += f"{value},***space***// p[{i}] {name}\n"
            vallen = len(str(value))
            max_vallen = vallen if max_vallen < vallen else max_vallen
        str_p = ""

        for line in str_p_with_replacement.splitlines():
            vallen = line.find(",")
            num_space = max_vallen - vallen + 1
            str_p += line.replace("***space***", " " * num_space) + "\n"

        self.y = str_ini_y[:-1]
        self.p = str_p[:-1]
        self.x = dict_x
