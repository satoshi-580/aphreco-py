import abc


class BaseItem(abc.ABC):
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        self._parent = parent

    def __str__(self):
        return f"{self.name}"

    def __iter__(self):
        return iter([])

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
    def _collect_names(self, names_dict):
        """collects names defined by Variable objects."""
        raise NotImplementedError

    @abc.abstractmethod
    def _collect_names_in_terms_recursively(self, used_names_set):
        raise NotImplementedError

    @abc.abstractmethod
    def copy(self, prefix, suffix, exclusive, share, _repmap):
        raise NotImplementedError

    @abc.abstractmethod
    def _get_item_by_name(self, name):
        raise NotImplementedError


class BaseComponent(BaseItem):
    def _get_item_by_name(self, name):
        if name == self.name:
            return self
        return None


class BaseEdge(BaseComponent):
    @abc.abstractmethod
    def _create_name_from_term(self, term):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_eq(self):
        raise NotImplementedError

    @abc.abstractmethod
    def collect_val(self):
        raise NotImplementedError
