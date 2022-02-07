from collections import OrderedDict
from typing import Dict, List, Optional, Set, Tuple

from aphreco.enums import ItemType

from .base import BaseEdge
from .func.rename import rename_all
from .func.symbolize import extract_symset, str_symbol_name


class BaseReg(BaseEdge):
    @property
    def beat(self):
        return self._beat

    @beat.setter
    def beat(self, beat):
        self._beat = beat


class ImplCollectForReg(BaseReg):
    def collect_names(self, _):
        pass

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        """collects all names used in terms and a beat of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        # beat
        used_names = {name for name in self.beat}
        # terms
        for yname, term in self.term.items():
            used_names.add(str_symbol_name(yname))
            symset = extract_symset(term)
            used_names = used_names | symset

        return used_names_set | used_names

    def collect_values(self):
        pass

    def collect_terms(self, terms_dict: Dict[str, Dict]) -> Dict[str, Dict]:
        rec = terms_dict["rec"]

        if self.beat not in rec.keys():
            rec[self.beat] = OrderedDict()

        for yname, rhs in self.term.items():
            if yname not in rec[self.beat].keys():
                rec[self.beat][yname] = rhs
            else:
                rec[self.beat][yname] += f" + {rhs}"

        terms_dict["rec"] = rec
        return terms_dict


class ImplRenameForReg(BaseReg):
    def _rename_self(self, repmap: Dict[str, str]):
        start, step, stop = self.beat
        if start in repmap.keys():
            start = repmap[start]
        if stop in repmap.keys():
            stop = repmap[stop]
        if step in repmap.keys():
            step = repmap[step]
        self.beat = (start, stop, step)

        renamed_term: Dict[str, str] = self.term.copy()
        for yname in self.term.keys():
            symset = extract_symset(renamed_term[yname])
            intersect = symset & repmap.keys()
            if intersect != set():
                for old in intersect:
                    renamed_term[yname] = rename_all(
                        term=renamed_term[yname],
                        old=old,
                        new=repmap[old],
                    )

            if yname in repmap.keys():
                new_name = repmap[yname]
                renamed_term[new_name] = renamed_term[yname]
                del renamed_term[yname]
        self.term = renamed_term

        if self._is_default_name:
            self._name = self._create_name_from_term(self.term)
        return self


class Reg(ImplCollectForReg, ImplRenameForReg, BaseEdge):
    """Reg represents a edge item connecting Y variables in a model.

    Attributes:
        beat (str, str, str): The tuple of three parameter names (start, stop, step),
            which defines discrete time points the edge term is calculated.

        term Dict[str, str]: The lhs and rhs of a recursive (difference) equation in a model.
            The key and value of the dictionary indicate a name of dependent variable (y) and
            a difference occuring at a discrete point (delta_y), respectively.

        name (str): The name of edge item in a model. If it is not designated in instanciation,
            it is automatically created from term.

        type (ItemType): The type of RegularBeat Edge ItemType.REG.

        parent (Model): The parent item.
    """

    def __init__(
        self,
        beat: Tuple[str, str, str],
        term: Dict[str, str],
        name: str = None,
        _is_default_name: bool = None,
    ):
        self.beat = beat
        self.term = term
        self._type = ItemType.REG
        self.parent = None

        if name is None:
            self._name = self._create_name_from_term(term)
            if _is_default_name is None:
                _is_default_name = True
        else:
            self._name = name
            if _is_default_name is None:
                _is_default_name = False

        self._is_default_name = _is_default_name

    def _create_name_from_term(self, term):
        str_from = ""
        str_to = ""
        for name, term in term.items():
            if term.lstrip()[0] == "-":
                str_from += "delta_" + name + "+=" + term + ","
            else:
                str_to += "delta_" + name + "+=" + term + ","
        name = f"{str_from[:-1]} -> {str_to[:-1]}"
        name = name.strip()
        return name

    def _add_or_skip(self, parent, is_done):
        edge = Reg(
            beat=self.beat,
            term=self.term,
            name=self.name,
            _is_default_name=self._is_default_name,
        )
        edge.parent = parent
        return edge, is_done

    def tree(
        self,
        indent: str = "",
        structure: Optional[List[str]] = None,
    ) -> Optional[List[str]]:
        if structure is None:
            structure = list()

        structure.append(f"{indent}[{self.type.name}] {self.name}")
        return structure

    def copy(
        self,
        prefix="",
        suffix="",
        exclusive: List[str] = [],
        share: bool = False,
        _repmap: Dict[str, str] = None,
    ):
        # beat
        start, stop, step = self.beat
        if _repmap is not None:
            if start in _repmap.keys():
                start = _repmap[start]
            if stop in _repmap.keys():
                stop = _repmap[stop]
            if step in _repmap.keys():
                step = _repmap[step]
        copied_beat = (start, stop, step)

        # term
        copied_term: Dict[str, str] = OrderedDict()
        for yname, str_rhs in self.term.items():
            # because lhs is always ItemType.Y,
            # add prefix/suffix to yname unconditionally.
            copied_name = prefix + yname + suffix

            copied_rhs = str_rhs
            if _repmap is not None:
                for old, new in _repmap.items():
                    copied_rhs = copied_rhs.replace(old, new)

            copied_term[copied_name] = copied_rhs

        if self.name != self._create_name_from_term(self.term):
            copied_name = self.name
        else:
            copied_name = None

        copied_edge = Reg(
            beat=copied_beat,
            term=copied_term,
            name=copied_name,
            _is_default_name=self._is_default_name,
        )

        return copied_edge

    def _delete_involved(self, name: str):
        """deletes an involved components in beat or term.

        If edge beat has a name to be deleted, the edge itself is to be deleted.
        """
        # beat
        start, step, stop = self.beat
        if (name == start) or (name == step) or (name == stop):
            return True, self

        # term
        del_term = self.term.copy()
        for yname in self.term.keys():
            # if name is included as a symbol in term,
            # the whole term is deleted.
            symset = extract_symset(del_term[yname])
            if name in symset:
                del del_term[yname]

        if name in del_term.keys():
            del del_term[name]

        self.term = del_term
        if len(self.term) > 0:
            is_empty = False
        else:
            is_empty = True

        if self._is_default_name and (not is_empty):
            self._name = self._create_name_from_term(self.term)

        return is_empty, self
