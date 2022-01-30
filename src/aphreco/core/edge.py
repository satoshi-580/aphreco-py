import abc

from .base import BaseComponent


class Edge(BaseComponent):
    @abc.abstractmethod
    def collect_eq(self):
        NotImplementedError

    @abc.abstractmethod
    def collect_val(self):
        NotImplementedError
