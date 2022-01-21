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
        self.x_index = ""
        self.x_bounds = ""
        self.obs = ""

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
                f"  act[{i}] = if *dec_t == next_t[{i}] {{ true }} else {{ false }};"
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
        self.y = str_ini_y[:-1]

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
        self.p = str_p[:-1]

        # assemble x
        str_x_index_with_replacement = ""
        str_x_bounds_with_replacement = ""
        max_vallen_index = 0
        max_vallen_bounds = 0
        for i, (name, (value, bounds)) in enumerate(dict_x.items()):
            # '//' is a comment format in Rust lang.
            index = symbols.member[name][1]
            str_x_index_with_replacement += (
                f"{index},***space***// x[{i}] {name} (= p[{index}])\n"
            )
            vallen_index = len(str(index))
            max_vallen_index = (
                vallen_index if max_vallen_index < vallen_index else max_vallen_index
            )

            str_x_bounds_with_replacement += (
                ""
                if bounds is None
                else f"{bounds},***space***// x[{i}] {name} (= p[{symbols.member[name][1]}])\n"
            )
            vallen_bounds = len(str(bounds))
            max_vallen_bounds = (
                vallen_bounds
                if max_vallen_bounds < vallen_bounds
                else max_vallen_bounds
            )

        str_x_index = ""
        for line in str_x_index_with_replacement.splitlines():
            vallen = line.find(",")
            num_space = max_vallen_index - vallen + 1
            str_x_index += line.replace("***space***", " " * num_space) + "\n"
        str_x_bounds = ""
        if len(str_x_bounds_with_replacement) == 0:
            str_x_bounds = "    let x_bounds = None;\n"
        else:
            for line in str_x_bounds_with_replacement.splitlines():
                vallen = line.find("),")
                num_space = max_vallen_bounds - vallen + 1
                str_x_bounds += line.replace("***space***", " " * num_space) + "\n"

        self.x_index = str_x_index
        self.x_bounds = str_x_bounds

    def collect_obs(self, obs):
        str_obs_with_replacement = ""
        max_datlen = 0
        for data in obs.data:
            str_dat = (
                "("
                + str(data[5])
                + ", "
                + str(data[1])
                + ", "
                + str(data[2])
                + ", "
                + str(data[3])
                + ", "
                + str(data[4])
                + ")"
            )
            str_obs_with_replacement += (
                str_dat + ",***space***// " + str(data[0]) + "\n"
            )
            datlen = len(str_dat)
            max_datlen = datlen if max_datlen < datlen else max_datlen

        str_obs = ""
        for line in str_obs_with_replacement.splitlines():
            datlen = line.find("),")
            num_space = max_datlen - datlen + 1
            str_obs += line.replace("***space***", " " * num_space) + "\n"

        self.obs = str_obs
