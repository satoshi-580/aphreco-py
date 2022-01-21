# Ready-made classes return a Unit object
# that contains an assembled model.
import abc

from aphreco.unit import Unit


class ReadyMade(abc.ABC):
    def new(cls) -> Unit:
        pass
