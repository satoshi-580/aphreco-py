# from aphreco.model import Model

from aphreco.utils import is_valid_name_str


class Unit:
  def __init__(self, name):
    if not is_valid_name_str(name):
      raise ValueError(f"'{name}' is invalid name.")

    self.name = name
    self.simulator = None
    self.optimizer = None
    self.data = None
    self.analyzer = None
