"""Unit class provides a modeling interface.
Unit: a modeling unit that contains methods for model construction
"""

from collections import deque
from typing import Any, List, Optional, Union

from aphreco.core import BaseComponent, BaseEdge, BaseItem, BaseModel, Box, Obs, Var
from aphreco.solve import (
    Command,
    OptCollector,
    Optimizer,
    OptWriter,
    Replacer,
    SimCollector,
    Simulator,
    SimWriter,
)
from aphreco.solve.optimize import NelderMead
from aphreco.solve.simulate import Dopri45
from aphreco.symbols import Symbols


class Unit:
    def __init__(self, name: str = "") -> None:
        self.symbols = Symbols()  # symbols for duplication check
        self.model = Box(name)  # model expressed as a tree structure
        self.simulator = Simulator(Dopri45())  # a simulation method and its options

        self.data = Obs()  # observation data
        self.optimizer = Optimizer(
            methods=[NelderMead()]
        )  # methods and the corresponding options

        self.flags = dict(data_loaded=False)

        self.add(Box(name="preset", mtype="blackbox"))
        presets = [
            Var(name="ini_t", vtype="p", value=0.0),
            Var(name="endless", vtype="p", value=1e14),
            Var(name="onlyonce", vtype="p", value=1e14),
        ]
        self.add(presets, path="/preset")

    def add(
        self,
        items: Union[BaseItem, List[Any]],
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
                f"invalid path: {model.type} found in '{path}'. expected Box."
            )

        if not isinstance(items, list):
            items = [items]

        for item in items:
            if not isinstance(item, BaseItem):
                raise ValueError(f"invalid item: {type(item)}")

            elif isinstance(item, BaseModel):
                model._add(item)

            elif isinstance(item, BaseComponent):
                new_symbol = item._get_symbols()

                if isinstance(item, BaseEdge):
                    for new_sym in new_symbol:
                        s = str(new_sym)
                        if not self.symbols.exists(s):
                            raise ValueError(f"There is no variable '{s}'.")
                else:
                    s = str(new_symbol)
                    self.symbols.add(s, item.type)
                model._add(item)

    def rename(self, name, new_name):
        pass

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

    def simulate(self, now=True):
        source = SimCollector.run(self.model, self.symbols, self.simulator)
        rep_source = Replacer.run(source, self.symbols)
        SimWriter().run(rep_source)
        if now:
            Command.run()

    def optimize(self, now=True):
        source = OptCollector.run(
            self.model, self.symbols, self.simulator, self.optimizer, self.data
        )
        rep_source = Replacer.run(source, self.symbols)
        OptWriter().run(rep_source)
        if now:
            Command.run()

    def read_data(self, path):
        self.data.read_obs(path)
        self.data.set_y_index(self.symbols)
        self.data.sort_by_index()

    def remove(self, name):
        target_path = self.find(name)
        if target_path is None:
            raise KeyError(f"{name} not found")
        # split
        dq_path = deque(target_path.split("/"))
        _ = dq_path.popleft()
        if len(dq_path) > 0:
            self.model._remove_by_name(dq_path)
