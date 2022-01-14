from aphreco.tree import Model
from aphreco.utils.name import is_valid_name_str


class Unit:
    def __init__(self, name):
        if not is_valid_name_str(name):
            raise ValueError(f"'{name}' is invalid name.")

        self.name = name
        self.simulator = None
        self.optimizer = None
        self.data = None
        self.analyzer = None
