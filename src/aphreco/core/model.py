import itertools
from collections import OrderedDict, deque
from typing import Dict, List, Optional, Set, Tuple, Union

from aphreco.enums import ItemType
from aphreco.errors import DuplicatedNameError, UnregisteredNameError

from .base import BaseEdge, BaseItem
from .func.collect import ImplCollectForModel
from .utils.colors import PColor

SEPARATOR = "\\"


class Model(ImplCollectForModel, BaseItem):
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
    """

    type = ItemType.MODEL

    def __init__(
        self,
        name="",
        items: Optional[Union[BaseItem, List[BaseItem]]] = None,
        hide=False,
    ):
        self.parent = None
        self._name = name
        self.hide = hide

        self.children: Dict[str, BaseItem] = OrderedDict()
        if items is not None:
            self.add(items)

    def __iter__(self):
        return iter(self.children.items())

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name: str):
        if self.parent is None:
            self._name = name
            return

        check_model_name_duplication(self.parent, name)
        self._name = name

        sibships: Dict[str, BaseItem] = OrderedDict()
        for _, item in self.parent.children.items():
            sibships[item.name] = item
        self.parent.children = sibships

    def add(self, items: Union[BaseItem, List[BaseItem]], duplicate: str = "error"):
        """adds items

        This method is not recursive, but calls a recursive self._add method inside.

        Args:
            new_items (Union[BaseItem, List[BaseItem]]): BaseItem(Model)

            duplicate (str): how to deal with items with a duplicated name.
                Duplication occurs in two ways; the first is inside the new_items,
                the second is between new_items and an original model.
                "error"; raise DuplicatedNameError
                "skip" ; skip adding and does not raise error
                    if duplication is inside new_items, the only first one is added (the priority is
                    given to the one registered earlier).
                    if duplication is between new_items and an origin, just skip all duplicated items.
        """

        if not isinstance(items, list):
            items = [items]

        # check new model name directly below self
        for item in items:
            if isinstance(item, Model):
                check_model_name_duplication(self, item.name)

        new_names_dict_list = self._collect_new_names(items)
        existing_names_dict = self._collect_existing_names()

        if not isinstance(duplicate, str):
            raise TypeError(f"not str found in 'dupliate': excpected 'error' or 'skip'")

        # check new variables
        elif duplicate == "error":
            # if new_items have duplicated names, raise error.
            check_duplication_within_new(new_names_dict_list)

            # compare names in new_items with the existing names
            check_duplication_between_new_and_old(
                new_names_dict_list,
                existing_names_dict,
            )
            is_done = None

        elif duplicate == "skip":
            union_new_names: Set[str] = set()
            for names_dict in new_names_dict_list:
                union_new_names = union_new_names | names_dict.keys()

            is_done = {name: False for name in list(union_new_names)}
            for key in existing_names_dict.keys() & is_done.keys():
                is_done[key] = True

        else:
            raise ValueError(f"invalid argument: {duplicate}")

        # check new edges
        used_names_set = self.collect_names_in_new_terms(items)
        check_unregistration(
            used_names_set,
            existing_names_dict,
            new_names_dict_list,
        )

        # add items
        for new_item in items:
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
            # does not collect from Edge
            if isinstance(new_item, BaseEdge):
                continue

            new_names_dict = new_item.collect_names(OrderedDict())
            new_names_dict_list.append(new_names_dict)

        return new_names_dict_list

    def collect_names_in_new_terms(self, new_items: List[BaseItem]):
        """
        Model._collect_names_in_terms() -> go to lower layers recursively
        Variable._collect_names_in_terms() -> return with no change
        Edge._collect_names_in_terms() -> collect
        """
        used_names_set: Set[str] = set()
        for new_item in new_items:
            used_names_set = used_names_set | new_item._collect_names_in_terms(
                used_names_set
            )
        return used_names_set

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        if len(self.children) == 0:
            return used_names_set

        for _, item in self.children.items():
            # collect from Edge and Variable with cre, or go to lower Model
            used_names_set = item._collect_names_in_terms(used_names_set)
        return used_names_set

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
            return self.collect_names(OrderedDict())
        else:
            return self.parent._collect_existing_names()

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        """creates a str list of tree components."""
        if structure is None:
            structure = list()

        if not self.hide:
            structure.append(f"{indent}{self.name}\\")
            for _, item in self:
                structure = item.tree(indent + "  ", structure)
        else:
            structure.append(f"{indent}{self.name}\\...")

        return structure

    def __str__(self):
        """connects a tree items via line feeds."""
        tree = list()
        for node in self.tree():
            if "[ Y ]" in node:
                tree.append(node.replace("[ Y ]", PColor.R + "[ Y ]" + PColor.RESET))
            elif "[CON]" in node:
                tree.append(node.replace("[CON]", PColor.B + "[CON]" + PColor.RESET))
            elif "[REG]" in node:
                tree.append(node.replace("[REG]", PColor.B + "[REG]" + PColor.RESET))
            else:
                tree.append(node)
        return "\n".join(tree)

    def copy(
        self,
        prefix="",
        suffix="",
        exclusive: List[str] = [],
        share: bool = True,
        _repmap: Dict[str, str] = None,
    ):
        """copies items recursively as adding prefix/suffix to names"""
        # create repmap Dict[old, new]
        existing_names_dict = self._collect_existing_names()
        if _repmap is None:
            _repmap = OrderedDict()

            for name, item in existing_names_dict.items():
                if item[0] == ItemType.Y:
                    _repmap[name] = prefix + name + suffix
                elif name in exclusive:
                    _repmap[name] = prefix + name + suffix
                elif share and not self[name].share:
                    _repmap[name] = prefix + name + suffix
                elif (not share) and (exclusive == []):
                    _repmap[name] = prefix + name + suffix
                else:
                    continue

        # sort by length of old names
        _repmap = OrderedDict(
            sorted(_repmap.items(), key=lambda k: len(k[0]), reverse=True)
        )

        # check duplication of names after adding prefix/suffix
        new_names_dict_list = [{new_name: None for _, new_name in _repmap.items()}]
        check_duplication_between_new_and_old(new_names_dict_list, existing_names_dict)

        # add prefix/suffix to a root Model.
        if self.parent is None:
            name = prefix + self.name + suffix
        else:
            name = self.name

        # construct copied_model
        copied_model = Model(name=name, hide=self.hide)
        copied_model.parent = self.parent

        for name, item in self.children.items():
            child = item.copy(prefix, suffix, exclusive, share, _repmap)
            copied_model.children[child.name] = child
            copied_model.children[child.name].parent = copied_model

        return copied_model

    def __getitem__(self, name: str):
        if SEPARATOR not in name:
            dq_path = self._find_path_by_name(name, deque([]))
            if dq_path is None:
                raise KeyError(f"'{name}' not found.")
            dq_path.popleft()

        else:
            dq_path = deque(name.split(sep=SEPARATOR))
            if dq_path[0] == "":
                dq_path.popleft()

        res = self._get_item_by_path(dq_path)
        if res is None:
            raise KeyError(f"'{name}' not found.")
        return res

    def _get_item_by_path(self, dq_path: deque):
        name = dq_path.popleft()
        if name == "":
            return self
        elif name not in self.children.keys():
            return None
        elif len(dq_path) == 0:
            return self.children[name]
        else:
            next_item = self.children[name]
            if isinstance(next_item, Model):
                return next_item._get_item_by_path(dq_path)
            return None

    def delete(self, name: str):
        if self.parent is not None:
            # go up to a top of a tree
            self.parent.delete(name)

        else:
            if SEPARATOR not in name:
                dq_path = self._find_path_by_name(name, deque([]))
                if dq_path is None:
                    raise KeyError(f"'{name}' not found.")
                dq_path.popleft()

            else:
                dq_path = deque(name.split(sep=SEPARATOR))
                if dq_path[0] == "":
                    dq_path.popleft()
                # check if the path is valid
                _ = self._get_item_by_path(dq_path.copy())

            del_name = dq_path[-1]
            self._delete_item_by_path(dq_path)
            self._delete_involved(del_name)

    def _delete_item_by_path(self, dq_path: deque):
        name = dq_path.popleft()
        if name not in self.children.keys():
            raise KeyError(f"'{name}' not found.")
        elif len(dq_path) == 0:
            del self.children[name]
        else:
            next_item = self.children[name]
            if isinstance(next_item, Model):
                next_item._delete_item_by_path(dq_path)
            else:
                raise KeyError(f"invalid path: '{dq_path[0]}'")

    def _delete_involved(self, name: str):
        lst_children = list()

        for _, item in self.children.items():
            is_empty, del_child = item._delete_involved(name)
            if is_empty:
                continue
            else:
                lst_children.append((del_child.name, del_child))

        self.children = OrderedDict(lst_children)

        return False, self

    def rename(self, repmap: Dict[str, str]):
        """renames an old name (key) into a new name (value) of repmap (dictionary)."""
        if self.parent is not None:
            # go upward to a top of a tree
            self.parent.rename(repmap)
        else:
            # if the current model is a top of a tree, start renaming

            # check duplication of renamed name
            existing_names_dict = self._collect_existing_names()
            new_names_dict_list = [
                {new_name: (ItemType.ITEM, -1) for _, new_name in repmap.items()}
            ]
            check_duplication_between_new_and_old(
                new_names_dict_list,
                existing_names_dict,
            )
            used_names_set = set(repmap.keys())
            check_unregistration(
                used_names_set,
                existing_names_dict,
                new_names_dict_list,
            )

            # rename
            self._rename_self(repmap)

    def _rename_self(self, repmap: Dict[str, str]):
        if self.name in repmap.keys():
            self._name = repmap[self.name]

        renamed_children: Dict[str, BaseItem] = OrderedDict()
        for _, item in self.children.items():
            renamed_child = item._rename_self(repmap)
            renamed_children[renamed_child.name] = renamed_child

        self.children = renamed_children

        return self

    def find(self, name: str) -> Optional[str]:
        if name == self.name:
            return name

        dq_path = self._find_path_by_name(name, deque([]))

        if dq_path is None:
            return None

        return SEPARATOR.join(dq_path)

    def _find_path_by_name(self, name: str, dq_path: deque) -> Optional[deque]:
        ans = None

        if name == self.name:
            dq_path.append(name)
            return dq_path

        for _, item in self.children.items():
            dq_path.append(self.name)
            ans = item._find_path_by_name(name, dq_path)
            if ans is None:
                dq_path.pop()
            else:
                break
        return ans

    def set_yp_index(
        self, names_dict: Dict[str, Tuple[ItemType, int]]
    ) -> Dict[str, Tuple[ItemType, int]]:
        y_index = 0
        p_index = 0
        for name, (itemtype, _) in names_dict.items():
            if itemtype == ItemType.Y:
                names_dict[name] = (itemtype, y_index)
                y_index += 1
            elif itemtype in (ItemType.P | ItemType.X):
                names_dict[name] = (itemtype, p_index)
                p_index += 1
            else:
                continue
        return names_dict

    def collect_values(self, val_dicts: Dict[str, Dict]) -> Dict[str, Dict]:
        """collects values of Variables in a model.

        Args:
            val_dicts Dict[str, Dict]: The dictionary of a name (key) and a value (value) of Variables.
                values Dict[str, value]: {"value", "lb", "ub"}
        """
        for _, item in self.children.items():
            if isinstance(item, BaseEdge):
                continue
            else:
                val_dicts = item.collect_values(val_dicts)
        return val_dicts

    def collect_terms(self, terms_dict: Dict[str, Dict]):
        return terms_dict


# class Model(BaseComponent):
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


def check_duplication_within_new(
    new_names_dict_list: List[Dict[str, Tuple[ItemType, int]]]
):
    """checks if there is any duplication of names inside new_items.

    Args:
        new_names_dict_list (List[Dict[str, (ItemType, int)]]): list of names_dict based on new_items
    """

    # In the case of length of new_names_dict_list >= 2,
    # name duplications for all combinations of list components will be checked.
    # if length of new_items is 1, the process does not reach to the inside of the for-loop.
    for a, b in itertools.combinations(new_names_dict_list, 2):
        intersection = a.keys() & b.keys()
        if intersection != set():
            raise DuplicatedNameError(intersection)


def check_duplication_between_new_and_old(
    new_names_dict_list,
    existing_names_dict: Dict[str, Tuple[ItemType, int]],
):
    """checks if the new_items have the name that has already existed.

    Args:
        new_items: List[Any of BaseItem]
    """
    # check duplication between new_items and items in the original model.
    union: Set[str] = set()
    for new in new_names_dict_list:
        union = union | new.keys()

    # if duplication is found, raise error.
    intersection = union & existing_names_dict.keys()
    if intersection != set():
        raise DuplicatedNameError(intersection)


def check_unregistration(
    used_names_set: Set[str],
    existing_names_dict: Dict[str, Tuple[ItemType, int]],
    new_names_dict_list: List[Dict[str, Tuple[ItemType, int]]],
):
    union: Set[str] = set()
    for new in new_names_dict_list:
        union = union | new.keys()
    union = union | existing_names_dict.keys()

    difference = used_names_set - union
    if difference != set():
        raise UnregisteredNameError(difference)


def check_model_name_duplication(model: Model, child_name: str):
    if child_name in model.children.keys():
        raise DuplicatedNameError(child_name)
