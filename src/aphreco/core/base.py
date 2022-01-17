import abc
import enum


class ItemType(enum.Flag):
    # Components
    Y = enum.auto()  # dependent variable
    P = enum.auto()  # constant model parameter
    X = enum.auto()  # unknown parameter in optimization
    VARIABLE = Y | P | X
    CON = enum.auto()  # continuous edge
    REG = enum.auto()  # discrete edge with a regular interval
    EDGE = CON | REG
    COMPONENT = VARIABLE | EDGE

    # Composite
    BOX = enum.auto()  # show inside
    BLACKBOX = enum.auto()  # hide inside if it has multiple type-Y objects
    MODEL = BOX | BLACKBOX


class BaseItem(abc.ABC):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, _):
        raise NotImplementedError

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, _):
        raise NotImplementedError

    def __iter__(self):
        return iter([])

    @abc.abstractmethod
    def _print_tree(self, indent):
        raise NotImplementedError


class BaseComponent(BaseItem):
    @abc.abstractmethod
    def _get_symbol(self):
        raise NotImplementedError


class BaseModel(BaseItem):
    @abc.abstractmethod
    def _get_item(self, dq_path):
        raise NotImplementedError

    @abc.abstractmethod
    def _find_name(self, name, path):
        raise NotImplementedError

    @abc.abstractmethod
    def _add(self, item):
        raise NotImplementedError

    @abc.abstractmethod
    def _formulate(self, eq_dicts):
        raise NotImplementedError
