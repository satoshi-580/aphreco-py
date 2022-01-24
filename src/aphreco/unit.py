from collections import deque
from typing import List, Optional, Union

from aphreco.command import Command
from aphreco.core import BaseComponent, BaseEdge, BaseItem, BaseModel, Box, Obs
from aphreco.enums import ProcType
from aphreco.solve import Optimizer, Simulator
from aphreco.symbols import Symbols
from aphreco.write import Source, Writer


class Unit:
    def __init__(self, name: str = "", ini_t: float = 0.0) -> None:
        self.symbols = Symbols()  # symbols for duplication check
        self.model = Box(name)  # model expressed as a tree structure
        self.simulator = Simulator()  # a simulation method and its options

        self.obs = Obs()  # observation data
        self.optimizer = Optimizer()  # methods and the corresponding options

        self.source = Source()  # harvest items from self.model
        self.writer = Writer()  # write/save code from model source
        self.command = Command()  # for rust compilation
        self.ini_t = ini_t
        self.flags = dict(data_loaded=False)

    @property
    def ini_t(self):
        return self._ini_t

    @ini_t.setter
    def ini_t(self, ini_t: float):
        self._ini_t = ini_t
        self.source.t = str(float(ini_t))

    def add(
        self,
        items: Union[BaseComponent, List[BaseComponent]],
        path: str = "/",
        name: str = None,
    ):
        """Add items to Unit.model"""
        # TODO: enable to add nested box items by Width-First Search
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

            if isinstance(item, BaseComponent):
                new_symbol = item._get_symbol()

                if isinstance(item, BaseEdge):
                    for new_sym in new_symbol:
                        s = str(new_sym)
                        if not self.symbols.exists(s):
                            raise ValueError(f"There is no variable '{s}'.")
                else:
                    s = str(new_symbol)
                    self.symbols.add(s, item.type)
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

    def simulate(self, now=True):
        self.collect(ProcType.SIM)
        self.write(ProcType.SIM)
        if now:
            self.command.compile()

    def optimize(self, now=True):
        self.collect(ProcType.OPT)
        self.write(ProcType.OPT)
        if now:
            self.command.compile()

    def collect(self, ptype: ProcType):
        if ptype in (ProcType.SIM | ProcType.OPT):
            # create
            #   source.ode: str
            #   source.rec: str
            #   source.cre: str
            self.source.collect_equations(self.model)

            # create
            #   source.y: str
            #   source.p: str
            self.source.collect_values(self.model, self.symbols)

        if ptype == ProcType.OPT:
            # create
            #   source.x: str
            #   source.obs
            self.source.collect_obs(self.obs)

    def write(self, ptype: ProcType):
        rust_code = self.writer.write(self.source, self.symbols, ptype)
        self.code_name = self.writer.save(rust_code)

    def read_obs(self, path):
        self.obs.read_obs(path)
        self.obs.set_y_index(self.symbols)
        self.obs.sort_by_index()

    def remove(self, name):
        target_path = self.find(name)
        if target_path is None:
            raise KeyError(f"{name} not found")
        # split
        dq_path = deque(target_path.split("/"))
        _ = dq_path.popleft()
        if len(dq_path) > 0:
            self.model._remove_by_name(dq_path)
