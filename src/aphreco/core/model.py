import itertools
from collections import OrderedDict
from typing import Dict, List, Optional, Set, Tuple, Union

from aphreco.core.base import BaseItem
from aphreco.core.variable import Variable
from aphreco.enums import ItemType
from aphreco.errors import NameDuplicationError


class Model(BaseItem):
    """Model represents a composite of items in a model tree.

    A Model object can contain objects of Variable, Edge, and Model itself.
    The items are included in self.children, so that a client can visit them recursively.

    Attributes:
        name (str): The name of model

        items (OrderedDict): a dictionary that contains
            children's name and objects

        type (ItemType): class member, ItemType.MODEL

        hide (bool): whether or not print children when printing the model structure

        parent (BaseItem): an upper layer item in a tree structure

    Example:
        >>> import aphreco as ap
        >>> model = ap.Model("sample")
        >>> model.name
        sample
    """

    type = ItemType.MODEL

    def __init__(
        self,
        name="",
        items: Optional[Union[BaseItem, List[BaseItem]]] = None,
        hide=False,
    ):
        self.name = name
        self.hide = hide
        self.parent = None

        if items is None:
            self.children: Dict[str, BaseItem] = OrderedDict()
        else:
            self.add(items)

    def __iter__(self):
        return iter(self.children.items())

    def add(self, new_items: Union[BaseItem, List[BaseItem]], duplicate: str = "error"):
        """adds items

        This method is not recursive, but calls a recursive self._add method inside.

        Args:
            new_items (Union[BaseItem, List[BaseItem]]): BaseItem(Model)

            duplicate (str): how to deal with items with a duplicated name.
                Duplication occurs in two ways; the first is inside the new_items,
                the second is between new_items and an original model.
                "error"; raise NameDuplicationError
                "skip" ; skip adding and does not raise error
                    if duplication is inside new_items, the only first one is added (the priority is
                    given to the one registered earlier).
                    if duplication is between new_items and an origin, just skip all duplicated items.
        """

        if not isinstance(new_items, list):
            new_items = [new_items]

        new_names_dict_list = self._collect_new_names(new_items)
        existing_names_dict = self._collect_existing_names()

        if not isinstance(duplicate, str):
            raise TypeError(f"duplicate expects str 'error' or 'skip'.")

        elif duplicate == "error":
            # if new_items have duplicated names, raise error.
            self.check_duplication_within_new(new_names_dict_list)

            # compare names in new_items with the existing names
            self.check_duplication_between_new_and_old(
                new_names_dict_list, existing_names_dict
            )
            is_done = None

        elif duplicate == "skip":
            new_names_set: Set[str] = set()
            for names_dict in new_names_dict_list:
                new_names_set = new_names_set | names_dict.keys()

            is_done = {name: False for name in list(new_names_set)}
            for key in existing_names_dict.keys() & is_done.keys():
                is_done[key] = True

        else:
            raise ValueError(f"invalid argument: {duplicate}")

        for new_item in new_items:
            child, is_done = new_item._add_or_skip(parent=self, is_done=is_done)
            if child is not None:
                self.children[child.name] = child

    def _add_or_skip(self, parent, is_done: Dict[str, bool]):
        """creates items recursively and returns a Model object with items in a lower layer.

        Args:
            parent (Model): An item (Model object) in an upper layer

            is_done (Dict[str, bool]): A dictionary that contains str of item names as key,
                and bool if addition has been done or not as value.
                The bool is used to judge if the addition of an item should be skipped or not.
                If True, skip; if False, add an item to Model.children.

        Returns:
            Optional[Model]: The Model object with children and with parent set.
                Addition of items with duplicated names to children are skipped.

            Dict[str, bool]: is_done updated in adding Variable objects
        """
        model = Model(name=self.name, hide=self.hide)
        model.parent = parent

        for name, item in self.children.items():
            child, is_done = item._add_or_skip(parent=model, is_done=is_done)
            if child is not None:
                model.children[name] = child
        return model, is_done

    def _collect_new_names(self, new_items: List[BaseItem]):
        """
        Model.collect_names(noargs) -> names_dict
        Variable.collect_names(names_dict) -> names_dict
        """
        # collect new_names from new_items
        new_names_dict_list = list()
        for new_item in new_items:
            new_names_dict = new_item._collect_names(OrderedDict())
            new_names_dict_list.append(new_names_dict)
        return new_names_dict_list

    def check_duplication_within_new(
        self, new_names_dict_list: List[Dict[str, Tuple[ItemType, int]]]
    ) -> bool:
        """checks if there is any duplication of names inside new_items.

        Args:
            new_names_dict_list (List[Dict[str, (ItemType, int)]]): list of names_dict based on new_items

        Returns:
            bool: always True meaning the new_names_dict_list passed the check.
                if not passed, raise NameDuplicationError.
        """

        # In the case of length of new_names_dict_list >= 2,
        # name duplications for all combinations of list components will be checked.
        # if length of new_items is 1, the process does not reach to the inside of the for-loop.
        for a, b in itertools.combinations(new_names_dict_list, 2):
            intersection = a.keys() & b.keys()
            if intersection != set():
                raise NameDuplicationError(intersection)
        return True

    def check_duplication_between_new_and_old(
        self, new_names_dict_list, existing_names_dict
    ) -> bool:
        """checks if the new_items have the name that has already existed.

        Args:
            new_items: List[Any of BaseItem]

        Returns:
            bool: This method always returns True because the process raises Error
                if the arg 'new_items' does not pass the check.
                The bool indicates if the new_items has passed the check or not.

        """
        # check duplication between new_items and items in the original model.
        union: Set[str] = set()
        for new in new_names_dict_list:
            union = union | new.keys()

        # if duplication is found, raise error.
        intersection = union & existing_names_dict.keys()
        if intersection != set():
            raise NameDuplicationError(intersection)

        return True

    def _collect_existing_names(self):
        """collects variable names in a model.

        Even though this method is called by a model in a middle layer,
        the method goes up to the top layer and start collecting names from a root model.

        Returns:
            Dict[str, (ItemType, int)]: names_dict with a name as a key, and
                a tuple of (itemtype, index) as value.
                All indices are set to -1 until Replacer.run().
                names_dict[name, (itemtype, index)]
        """
        if self.parent is None:
            return self._collect_names(OrderedDict())
        else:
            return self.parent._collect_existing_names()

    def _collect_names(self, names_dict: Dict[str, Tuple[ItemType, int]]):
        """recursively collects names of Y, P, X, E in lower layers than the current model.

        This method is an abstractmethod defined in and forced by BaseItem.
        Variable and Edge classes also have this method.
        The names collected in this method does not collect Model.name,
        because Model.name is not needed to be unique in a whole tree;
        Duplication of Model.names in a whole tree does not matter as long as
        it is unique within a single model.

        Args:
            names_dict (OrderedDict[str, (ItemType, int)]): The argument in which
                the function collects and stores tree items.
                The key of this dictionary indicates the name of Variable (str), and
                the value of this dictionary is a tuple of ItemType and index in Y or P.
                All indices are set to -1 in the collection phase and
                will be update in replacement phase.
        """
        if len(self.children) == 0:
            return names_dict

        for _, item in self.children.items():
            names_dict = item._collect_names(names_dict)
        return names_dict

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        """creates a str list of tree components."""
        if structure is None:
            structure = list()

        if not self.hide:
            structure.append(f"{indent}{self.name}/")
            for _, item in self:
                structure = item.tree(indent + "  ", structure)
        else:
            structure.append(f"{indent}{self.name}/...")

        return structure

    def __str__(self):
        return "\n".join(self.tree())

    def copy(self, prefix="", suffix="", exclusive=[], share=True):
        """copies items recursively as adding prefix/suffix to names"""
        if self.parent is None:
            name = prefix + self.name + suffix
        else:
            name = self.name

        model = Model(name=name, hide=self.hide)
        model.parent = self.parent
        for name, item in self.children.items():
            model.children[name] = item.copy(prefix, suffix, exclusive, share)
        return model

    def __getitem__(self, name: str):
        res = self._get_item_by_name(name)
        if res is None:
            raise KeyError(f"'{name}' not found.")
        return res

    def _get_item_by_name(self, name: str):
        if name == self.name:
            return self
        else:
            for _, item in self.children.items():
                res = item._get_item_by_name(name)
                if res is not None:
                    break
        return res


# from collections import OrderedDict, deque
# from typing import Dict, Optional

# from aphreco.enums import ItemType

# from .base import BaseComponent
# from .variable import Var


# class Model(BaseComponent):
#     def __init__(
#         self,
#         name: str,
#     ):
#         self.name = name
#         self.type = mtype
#         self.items: Dict[str, BaseItem] = OrderedDict()

#     def __iter__(self):
#         return iter(self.items.items())

#     @property
#     def name(self):
#         return self._name

#     @name.setter
#     def name(self, name: str):
#         self._name = name

#     @property
#     def type(self):
#         return self._type

#     @type.setter
#     def type(self, mtype: str):
#         if mtype not in MTYPES.keys():
#             raise ValueError(
#                 f"invalid model type: {mtype} \
#                 \nmtype must be chosen from {tuple(MTYPES.keys())}"
#             )
#         self._type = MTYPES[mtype]

#     def _print_tree(self, indent=""):
#         if self.type == ItemType.BOX:
#             print(f"{indent}{self}/")
#             for _, item in self:
#                 item._print_tree(indent + "  ")
#         elif self.type == ItemType.BLACKBOX:
#             print(f"{indent}{self}/...")

#     def _get_item(self, dq_path: deque) -> Optional[BaseItem]:
#         name = dq_path.popleft()
#         if name not in self.items.keys():
#             return None
#         elif len(dq_path) == 0:
#             return self.items[name]
#         else:
#             next_item = self.items[name]
#             if isinstance(next_item, (Var, BaseEdge)):
#                 raise ValueError(f"item '{name}' is a component, not a model")
#             elif isinstance(next_item, BaseModel):
#                 return next_item._get_item(dq_path)
#             else:
#                 return None

#     def _add(self, item: BaseItem, symbols: Optional[Symbols] = None):
#         if symbols is None:
#             self.items[item.name] = item
#         else:
#             print(str(item), symbols.exists(str(item)))

#     def _find_name(self, name, path: str) -> Optional[str]:
#         ans = None
#         for key, item in self:
#             if key == name:
#                 ans = f"{path}{self._name}/"
#                 break
#             elif isinstance(item, BaseModel):
#                 ans = item._find_name(name, f"{path}{self._name}/")
#                 if ans is not None:
#                     break
#         return ans

#     def _formulate(self, eq_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         """Collect terms of Edge objects or cre in Y objects by Depth-First Search.
#         eq_dicts: Dict['ode': dict_ode, 'rec': dict_rec, 'cre': dict_cre]
#             dict_ode: Dict[lhs, rhs]
#             dict_rec: Dict[(start, stop, step): Dict[lhs, rhs]]
#             dict_cre: Dict[lhs, rhs]
#         """
#         for _, item in self:
#             if isinstance(item, BaseModel):
#                 eq_dicts = item._formulate(eq_dicts)
#             elif isinstance(item, Var):
#                 eq_dicts = item._formulate(eq_dicts)
#             elif isinstance(item, BaseEdge):
#                 eq_dicts = item._formulate(eq_dicts)
#         return eq_dicts

#     def _collect_values(self, val_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
#         """Collect values of Var objects in a model by Depth-First Search.
#         val_dicts: Dict['y': dict_y, 'p': dict_p, 'x': dict_x]
#             dict_y: Dict[name, y0 (initial state value)]
#             dict_p: Dict[name, p (constant value)]
#             dict_x: Dict[name, (value, bounds)]
#         """
#         for _, item in self:
#             if isinstance(item, BaseModel):
#                 val_dicts = item._collect_values(val_dicts)
#             elif isinstance(item, Var):
#                 val_dicts = item._collect_values(val_dicts)
#             elif isinstance(item, BaseEdge):
#                 continue
#         return val_dicts
