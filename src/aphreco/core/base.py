import abc
from collections import deque
from typing import Optional


class BaseItem(abc.ABC):
    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def __str__(self):
        return f"{self.name}"

    @abc.abstractmethod
    def _add_or_skip(self, parent, is_done):
        """creates a BaseItem object to be added, or else skip.

        if Model, _add method creates items recursively and
        returns an object with items in a lower layer.
        if Component like Variable and Edge, _add methods creates just a Self object.

        If the object should be skipped, returns None.

        Args:
            parent (Model): An item (Model object) in an upper layer

            is_done (Dict[str, bool]): A dictionary that contains str of item names as key,
                and bool if addition has been done or not as value.
                The bool is used to judge if the addition of an item should be skipped or not.
                If True, skip; if False, add an item to Model.children.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def tree(self, indent, structure):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_names(self, names_dict):
        """collects names defined by Variable objects."""
        raise NotImplementedError

    @abc.abstractmethod
    def collect_values(self, vals_dict):
        """collects {names: values} of Variables."""
        raise NotImplementedError

    @abc.abstractmethod
    def collect_terms(self, terms_dict):
        """collects terms in Edges(for ode/rec) or Variable(for cre)."""
        raise NotImplementedError

    @abc.abstractmethod
    def _collect_names_in_terms(self, used_names_set):
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self, prefix, suffix, exclusive, share, _repmap):
        raise NotImplementedError

    @abc.abstractmethod
    def _rename_self(self, repmap):
        raise NotImplementedError

    @abc.abstractmethod
    def _find_path_by_name(self, name, dq_path):
        raise NotImplementedError

    @abc.abstractmethod
    def _delete_involved(self, name):
        raise NotImplementedError

    @abc.abstractmethod
    def set_values(self, vals_dict):
        raise NotImplementedError


class BaseComponent(BaseItem):
    def _find_path_by_name(self, name: str, dq_path: deque) -> Optional[deque]:
        if name == self.name:
            dq_path.append(self.name)
            return dq_path
        else:
            return None

    @property
    def term(self):
        return self._term

    @term.setter
    def term(self, term):
        self._term = term


class BaseEdge(BaseComponent):
    @abc.abstractmethod
    def _create_name_from_term(self, term):
        raise NotImplementedError

    @property
    def _is_default_name(self):
        return self.__is_default_name

    @_is_default_name.setter
    def _is_default_name(self, _is_default_name):
        self.__is_default_name = _is_default_name

    def set_values(self, _):
        pass
