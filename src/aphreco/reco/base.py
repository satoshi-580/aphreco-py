import abc

from aphreco.core import Model


class BaseModule(abc.ABC):
    # Module class returns a pre-assembled Model object.
    def __new__(cls, **args) -> Model:
        raise NotImplementedError
