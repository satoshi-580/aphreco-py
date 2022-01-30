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
    def _print(self, indent):
        raise NotImplementedError

    @abc.abstractmethod
    def _collect_names(self, result):
        raise NotImplementedError


class BaseComponent(BaseItem):
    pass
    # @abc.abstractmethod
    # def _get_ref_names(self):
    #     raise NotImplementedError
