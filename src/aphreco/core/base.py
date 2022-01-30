import abc


class BaseItem(abc.ABC):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    def __str__(self):
        return f"{self.name}"

    def __iter__(self):
        return iter([])

    @abc.abstractmethod
    def print(self, indent):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_names(self, result):
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self, prefix, suffix, exclusive, share):
        raise NotImplementedError


class BaseComponent(BaseItem):
    pass
    # @abc.abstractmethod
    # def _get_ref_names(self):
    #     raise NotImplementedError


class BaseEdge(BaseComponent):
    @abc.abstractmethod
    def collect_eq(self):
        NotImplementedError

    @abc.abstractmethod
    def collect_val(self):
        NotImplementedError
