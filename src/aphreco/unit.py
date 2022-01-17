from collections import deque
from pathlib import Path
from typing import List, Optional, Set, Union

import sympy

from aphreco.command import Command
from aphreco.core import BaseComponent, BaseEdge, BaseItem, BaseModel, Box
from aphreco.pick import Picker
from aphreco.write import Writer


class Unit:
    def __init__(self, name: str = "", ini_t: float = 0.0):
        self.model = Box(name)
        self.symbols: Set[str] = set()
        self.command = Command()
        self.writer = Writer()
        self.picker = Picker()
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

    def pick(self):
        # create
        #   picker.ode: str
        #   picker.rec: str
        #   picker.cre: str
        self.picker.collect_equations(self.model)
        # create
        #   picker.ini_y: str
        #   picker.p: str
        #   picker.ini_x: str
        self.picker.collect_values(self.model)

    def write(self):
        main_code = self.writer.rs_main()
        ode_code = self.writer.rs_ode(self.picker.ode)
        rec_code = self.writer.rs_rec(self.picker.rec)
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
