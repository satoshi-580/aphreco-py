import abc
import enum

class TypeC(enum.Flag):
  MODEL = enum.auto()
  CMPT = enum.auto()
  VAR = enum.auto()
  EDGE = enum.auto()


class BaseComponent(abc.ABC):
  @property
  def name(self):
    return self._name

  @name.setter
  def name(self, name):
    self._name = name
  
  def __iter__(self):
    return iter([])
  
  @abc.abstractmethod
  def _print_tree(self, indent=""):
    raise NotImplementedError

  # TODO: method delete/find/move/rename/duplicate
