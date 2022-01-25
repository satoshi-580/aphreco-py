import abc

from aphreco.unit import Unit


class BaseTemplate(abc.ABC):
    # Template classes return a Unit object that contains an pre-assembled model.
    def new(cls) -> Unit:
        pass
