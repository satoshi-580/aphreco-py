from collections import OrderedDict
from typing import Dict, List, Optional, Set, Union

from aphreco.enums import EqType, ItemType
from aphreco.types import Beat, Inline, TermsDicts

from .base import BaseEdge

EQTYPE = {
    "ode": EqType.ODE,
    "rec": EqType.REC,
    "cre": EqType.CRE,
}


class BaseStr(BaseEdge):
    @property
    def eqtype(self):
        return self._eqtype

    @eqtype.setter
    def eqtype(self, eqtype: Union[str, EqType]):
        if isinstance(eqtype, EqType):
            self._eqtype = eqtype
        else:
            if eqtype not in EQTYPE.keys():
                raise KeyError(f"invlaid eqtype: '{eqtype}'")
            self._eqtype = EQTYPE[eqtype]

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type

    @property
    def beat(self):
        return self._beat

    @beat.setter
    def beat(self, beat):
        self._beat = beat

    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, line: str):
        self._line = line

    @property
    def involve(self):
        return self._involve

    @involve.setter
    def involve(self, involve: List[str]):
        self._involve = involve


class ImplCollectForStr(BaseStr):
    def collect_names(self, _):
        pass

    def _collect_names_in_terms(self, used_names_set: Set[str]):
        """collects all names used in terms and a beat of this edge.

        This method is called when this object is added to a model
        to check if unregistered names are used in terms of this edge or not.
        """
        if self.beat is not None:
            used_names = {name for name in self.beat}
        else:
            used_names = set()

        if self.involve is not None:
            involved_names = {name for name in self.involve}
        else:
            involved_names = set()

        return used_names_set | used_names | involved_names

    def collect_values(self):
        pass

    def collect_terms(self, terms_dict: TermsDicts) -> TermsDicts:
        if self.eqtype == EqType.ODE:
            ode = terms_dict[0]
            if self.name not in ode.keys():
                ode[self.name] = [Inline(self.line)]
            else:
                ode[self.name].append(self.line)
            return (ode, terms_dict[1], terms_dict[2])

        elif self.eqtype == EqType.REC:
            rec = terms_dict[1]
            # register self.beat if it is encountered for the first time
            if self.beat not in rec.keys():
                rec[self.beat] = OrderedDict()

            if self.name not in rec[self.beat].keys():
                rec[self.beat][self.name] = [Inline(self.line)]

            else:
                raise NameError(f"not a unique name '{self.name}'")
            return (terms_dict[0], rec, terms_dict[2])

        elif self.eqtype == EqType.CRE:
            cre = terms_dict[2]
            if self.name not in cre.keys():
                cre[self.name] = Inline(self.line)
            else:
                raise NameError(f"not a unique name '{self.name}'.")

            return (terms_dict[0], terms_dict[1], cre)

        return terms_dict


class ImplRenameForStr(BaseStr):
    def _rename_self(self, repmap: Dict[str, str]):
        start, step, stop = self.beat
        if start in repmap.keys():
            start = repmap[start]
        if stop in repmap.keys():
            stop = repmap[stop]
        if step in repmap.keys():
            step = repmap[step]
        self.beat = (start, stop, step)

        renamed_involve: List[str] = self.involve
        for i, yname in enumerate(self.involve):
            if yname in repmap.keys():
                new_yname = repmap[yname]
                renamed_involve[i] = new_yname
                self.line = self.line.replace(yname, new_yname)

        self.involve = renamed_involve
        return self


class Str(ImplCollectForStr, ImplRenameForStr, BaseStr):
    def __init__(
        self,
        eqtype: str,
        name: str,
        line: str,
        involve: List[str] = None,
        beat: Beat = None,
    ):
        self.eqtype = eqtype
        self.type = ItemType.STR
        self.parent = None

        self._name = name
        self._is_default_name = True

        self.involve = involve
        self.line = line

        if self.eqtype == EqType.REC:
            if beat is None:
                raise ValueError("argument 'beat' is needed for FuncType.REC")
            self.beat = beat
        else:
            self.beat = None

    def _add_or_skip(self, parent, is_done):
        edge = Str(
            eqtype=self.eqtype,
            name=self.name,
            line=self.line,
            involve=self.involve,
            beat=self.beat,
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
        _is_top: bool = False,
    ):
        if _repmap is not None:
            if self.name in _repmap.keys():
                self._name = _repmap[self.name]
        return self

    def _delete_involved(self, name: str):
        """deletes an involved components in beat or term.

        If edge beat has a name to be deleted, the edge itself is to be deleted.
        """
        if self.beat is not None:
            start, step, stop = self.beat
            if (name == start) or (name == step) or (name == stop):
                return True, self

        if name in self.involve:
            return True, self

        return False, self
