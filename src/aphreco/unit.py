from collections import OrderedDict, deque
from pathlib import Path
from typing import Any, List, Optional, Set, Union

import sympy

from aphreco.command import Command
from aphreco.core import BaseComponent, BaseItem, BaseModel, Box, Edge
from aphreco.write import Writer


class Unit:
    def __init__(self, name: str = ""):
        self.model = Box(name)
        self.symbols: Set[Any] = set()
        self.command = Command()
        self.writer = Writer()

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
                f"invalid path: expected ItemType.SUBMODEL, found {model.type}."
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

                if isinstance(item, Edge):
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
        dict_ode, dict_rec = self.model._formulate(OrderedDict(), OrderedDict())

        str_ode = ""
        for lhs, rhs in dict_ode.items():
            eq = "deriv_" + lhs + " = " + str(sympy.sympify(rhs))
            str_ode += eq + "\n"

        str_rec = ""
        for lhs, rhs in dict_rec.items():
            pass

        self.ode = str_ode[:-1]
        self.rec = str_rec[:-1]

    def write(self):
        main_code = self.writer.rs_main()
        ode_code = self.writer.rs_ode(self.ode)
        model_code = self.writer.rs_sim_model(ode_code)
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
