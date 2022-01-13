import abc
from optparse import Option
from typing import Dict, Optional


class BaseComponent(abc.ABC):
  """Base class of components."""
  @abc.abstractproperty
  def type(self):
    pass

  def __iter__(self):
    return iter([])


class BaseModel(BaseComponent):
  def __init__(self, name: str, components: Optional[Dict[str, "BaseComponent"]]=None):
    self._name: str = name
    self.components = []
    if components:
      self.add(components)

  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, name):
    if self.has_name(name):
      raise ValueError(f"The name '{name}' has already been used.")
    else:
      self._name = name

  def __iter__(self):
    return iter(self.components)
