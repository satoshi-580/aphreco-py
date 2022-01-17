from collections import OrderedDict, deque
from pathlib import Path
from typing import List, Optional, Set, Union

import sympy

from aphreco.command import Command
from aphreco.core import BaseComponent, BaseEdge, BaseItem, BaseModel, Box
from aphreco.write import Writer


class Unit:
    def __init__(self, name: str = "", ini_t: float = 0.0):
        self.model = Box(name)
        self.symbols: Set[str] = set()
        self.command = Command()
        self.writer = Writer()
        self.ini_t = ini_t

    def add(
        self,
        items: Union[BaseComponent, List[BaseComponent]],
        path: str = "/",
        name: str = None,
    ):
        """Add items to Unit.model"""
        if name:
            model = self.get(name=name)
        else:
            model = self.get(path=path)

        if model is None:
            raise ValueError(f"invalid path: {path}")
        if not isinstance(model, BaseModel):
            raise ValueError(
                f"invalid path: expected ItemType.MODEL, found {model.type}."
            )

        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, BaseItem):
                raise ValueError(f"invalid item: {type(item)}")

            elif isinstance(item, BaseModel):
                model._add(item)

            if isinstance(item, BaseComponent):
                new_symbol = item._get_symbol()

                if isinstance(item, BaseEdge):
                    for new_sym in new_symbol:
                        s = str(new_sym)
                        self.check_symbols_used_in_edge(s)
                        self.symbols.add(s)
                else:
                    s = str(new_symbol)
                    self.check_new_symbol(s)
                    self.symbols.add(s)
                model._add(item)

    def get(self, name: Optional[str] = None, path: Optional[str] = None):
        # get item
        if name is None and path is None:
            raise ValueError("please designate name or path.")
        elif path is None:
            item_path = self.find(name)
            if item_path is None:
                raise ValueError(f"invalid path: {path}")
            path = item_path

        # Root item
        if path == "/":
            return self.model

        # Convert a path from string into deque
        path = path.strip("/")
        dq_path = deque(path.split("/"))
        return self.model._get_item(dq_path)

    def find(self, name: Optional[str]) -> Optional[str]:
        """
        Return:
            Path [str] if found,
            None if not found.
        """
        if name is None:
            raise ValueError("None found in name.")

        if self.model.name == name:
            return name
        else:
            path: Optional[str] = self.model._find_name(name=name, path="")
            if path is None:
                return None
            else:
                return path + name

    def tree(self):
        self.model._print_tree(indent="")

    def formulate(self):
        self.collect_equations()
        self.collect_values()

    def collect_equations(self):
        # dict_ode: Dict[lhs('deriv_' not yet added), rhs]
        # dict_rec: Dict[(start, stop, step), Dict[lhs('delta_' not yet added), rhs]]
        # dict_cre: Dict[lhs, rhs]
        eq_dicts = self.model._formulate(
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

        # assemble rec
        str_rec = ""
        for i, (beat, rec) in enumerate(dict_rec.items()):
            str_rec += f"=== {i}: {beat}\n"
            for lhs, rhs in rec.items():
                eq = "delta_" + lhs + " += " + str(sympy.sympify(rhs))
                str_rec += eq + "\n"

        # assemble cre
        str_cre = ""
        for lhs, rhs in dict_cre.items():
            eq = lhs + " = " + str(sympy.sympify(rhs))
            str_cre += eq + "\n"

        self.ode = str_ode[:-1]
        self.rec = str_rec[:-1]
        self.cre = str_cre[:-1]

    def collect_values(self):
        val_dicts = self.model._collect_values(
            OrderedDict(y=OrderedDict(), p=OrderedDict(), x=OrderedDict())
        )
        dict_y = val_dicts["y"]
        dict_p = val_dicts["p"]
        dict_x = val_dicts["x"]

        # assemble y
        str_ini_y_with_replacement = ""
        max_vallen = 0
        for i, (name, value) in enumerate(dict_y.items()):
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
            # '//' is a comment format in Rust lang.
            str_p_with_replacement += f"{value},***space***// p[{i}] {name}\n"
            vallen = len(str(value))
            max_vallen = vallen if max_vallen < vallen else max_vallen
        str_p = ""

        for line in str_p_with_replacement.splitlines():
            vallen = line.find(",")
            num_space = max_vallen - vallen + 1
            str_p += line.replace("***space***", " " * num_space) + "\n"

        self.ini_y = str_ini_y[:-1]
        self.p = str_p[:-1]
        self.dict_x = dict_x

    def write(self):
        main_code = self.writer.rs_main()
        ode_code = self.writer.rs_ode(self.ode)
        rec_code = self.writer.rs_rec(self.rec)
        model_code = self.writer.rs_sim_model(ode_code, rec_code)
        rust_code = main_code + model_code
        file_name = "main.rs"
        with open(file_name, "w") as f:
            f.write(rust_code)

    def remove(self, name):
        target_path = self.find(name)
        if target_path is None:
            raise KeyError(f"{name} not found")
        # split
        dq_path = deque(target_path.split("/"))
        _ = dq_path.popleft()
        if len(dq_path) > 0:
            self.model._remove_by_name(dq_path)

    def check_symbols_used_in_edge(self, used_sym):
        if used_sym not in self.symbols:
            raise ValueError(f"There is no variable '{used_sym}'.")

    def check_new_symbol(self, new_sym):
        if new_sym in self.symbols:
            raise ValueError(f"The name '{new_sym}' has already been used.")
