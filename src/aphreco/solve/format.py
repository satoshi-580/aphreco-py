import abc
from typing import Dict, List, Tuple

import sympy
from aphreco.enums import ItemType


def _replace_space(lines: List[str], sub: str, max_vallen: int) -> List[str]:
    for i, line in enumerate(lines):
        vallen = line.find(sub)
        num_space = max_vallen - vallen + 1
        lines[i] = line.replace("***space***", " " * num_space)
    return lines


def _sympify_simplify(rhs: str, simplify_eq: bool) -> str:
    if simplify_eq:
        rhs = str(sympy.simplify(sympy.sympify(rhs)))
    else:
        rhs = str(sympy.sympify(rhs))
    return rhs


class BaseFormatter(abc.ABC):
    @property
    def simplify_eq(self):
        return self._simplify_eq

    @simplify_eq.setter
    def simplify_eq(self, simplify_eq):
        self._simplify_eq = simplify_eq


class SimFormatter(BaseFormatter):
    """"""

    def __init__(self, simplify_eq=False):
        self.simplify_eq = simplify_eq

    def line_y(
        self,
        names_dict: Dict[str, Tuple[ItemType, int]],
        vals_dict: Dict[str, float],
    ) -> str:
        return self._line_yp(names_dict, vals_dict, ItemType.Y)

    def line_p(
        self,
        names_dict: Dict[str, Tuple[ItemType, int]],
        vals_dict: Dict[str, float],
    ) -> str:
        return self._line_yp(names_dict, vals_dict, (ItemType.P | ItemType.X))

    def _line_yp(
        self,
        names_dict: Dict[str, Tuple[ItemType, int]],
        vals_dict: Dict[str, float],
        cur_type: ItemType,
    ):
        yp = "y" if cur_type == ItemType.Y else "p"
        lines = list()
        max_vallen = 0
        for name, (itemtype, index) in names_dict.items():
            if itemtype in cur_type:
                # '//' indicates a comment in Rust lang.
                lines.append(f"{vals_dict[name]},***space***// {yp}[{index}] {name}\n")
                vallen = len(str(vals_dict[name]))
                max_vallen = vallen if max_vallen < vallen else max_vallen

        lines = _replace_space(lines, ",", max_vallen)
        return "".join(lines)

    def arrange_ode(self, ode_dict: Dict[str, str]) -> str:
        lines = list()
        for lhs, rhs in ode_dict.items():
            rhs = _sympify_simplify(rhs, self.simplify_eq)
            eq = "deriv_" + lhs + " = " + rhs + "\n"
            lines.append(eq)
        return "".join(lines)

    def arrange_rec(
        self, rec_dict: Dict[Tuple[str, str, str], Dict[str, str]]
    ) -> Tuple[str, str, str]:

        rec_lines = list()
        cond_lines = list()
        beat_lines = list()

        for i, (beat, rec) in enumerate(rec_dict.items()):
            # rec
            rec_lines.append(f"=== {i}: {beat}\n")
            for lhs, rhs in rec.items():
                rhs = _sympify_simplify(rhs, self.simplify_eq)
                rec_line = "delta_" + lhs + " += " + rhs + "\n"
                rec_lines.append(rec_line)

            # condition
            cond_lines.append(
                f"act[{i}] = if *dec_t == next_t[{i}] {{ true }} else {{ false }}\n"
            )

            # beat
            beat_lines.append(
                "beat![" + beat[0] + ", " + beat[1] + ", " + beat[2] + "],\n"
            )

        str_rec = "".join(rec_lines)
        str_cond = "".join(cond_lines)
        str_beat = "".join(beat_lines)
        return str_rec, str_cond, str_beat

    def arrange_cre(self, cre_dict: Dict[str, str]) -> str:
        lines = list()
        for lhs, rhs in cre_dict.items():
            rhs = _sympify_simplify(rhs, self.simplify_eq)
            eq = lhs + " = " + rhs + "\n"
            lines.append(eq)
        return "".join(lines)


# import sympy
# from aphreco.core import BaseModel, Obs
# from aphreco.symbols import Symbols

# from .optimize.base import Optimizer
# from .simulate.base import Simulator
# from .source import Source


# class BaseCollector(abc.ABC):
#     """Collector recieves Unit.model and Unit.symbols, and returns a Source object."""

#     @classmethod
#     def _common_with_inherited(
#         cls,
#         source: Source,
#         model: BaseModel,
#         symbols: Symbols,
#         simulator: Simulator,
#         optimizer: Optional[Optimizer],
#     ):
#         NotImplementedError


# class SimCollector(BaseCollector):
#     @classmethod
#     def _common_with_inherited(
#         cls,
#         source: Source,
#         model: BaseModel,
#         symbols: Symbols,
#         simulator: Simulator,
#         _: Optional[Optimizer] = None,
#     ):
#         eq_dicts = cls.collect_eqdicts(model)

#         source.lines["ode"] = cls.arrange_ode(eq_dicts["ode"])

#         str_rec, str_cond, str_beat = cls.arrange_rec(eq_dicts["rec"])
#         source.lines["rec"] = str_rec
#         source.lines["cond"] = str_cond
#         source.lines["beat"] = str_beat

#         source.lines["cre"] = cls.arrange_cre(eq_dicts["cre"])

#         val_dicts = cls.collect_values(model)
#         source.lines["t"] = str(val_dicts["p"]["ini_t"])
#         source.lines["y"] = cls.arrange_y(val_dicts["y"], symbols)
#         source.lines["p"] = cls.arrange_p(val_dicts["p"], symbols)

#         stepper, stepper_options = cls.collect_simulator(simulator)
#         source.lines["stepper"] = stepper
#         source.lines["stepper_options"] = stepper_options
#         return source, eq_dicts, val_dicts


#     @classmethod
#     def collect_simulator(cls, simulator: Simulator):
#         """
#         simulator: Simulator
#             .options: Dict[str, value]
#         """
#         if simulator.stepper.is_default:
#             stepper_options = "default"
#         else:
#             stepper_options = ""
#             for key, value in simulator.stepper.options.items():
#                 if isinstance(value, bool):
#                     value = str(value).lower()
#                 stepper_options += key + ": " + str(value) + ",\n"
#         return simulator.stepper.name, stepper_options

#     @classmethod
#     def run(
#         cls,
#         model: BaseModel,
#         symbols: Symbols,
#         simulator: Simulator,
#     ) -> Source:
#         source = Source()
#         source, _, _ = cls._common_with_inherited(source, model, symbols, simulator)
#         return source


# class OptCollector(SimCollector):
#     @classmethod
#     def _common_with_inherited(
#         cls,
#         source: Source,
#         model: BaseModel,
#         symbols: Symbols,
#         simulator: Simulator,
#         optimizer: Optional[Optimizer] = None,
#     ):
#         source, _, val_dicts = super()._common_with_inherited(
#             source, model, symbols, simulator, optimizer
#         )
#         source.lines["x_index"] = cls.arrange_x_index(val_dicts["x"], symbols)
#         source.lines["x_bounds"] = cls.arrange_x_bounds(val_dicts["x"], symbols)

#         if optimizer is None:
#             raise ValueError("None found in optimizer")

#         lst_optimizer, lst_optimizer_options = cls.collect_optimizer(optimizer)
#         source.lines["optimizer"] = lst_optimizer
#         source.lines["optimizer_options"] = lst_optimizer_options

#         return source

#     @classmethod
#     def arrange_x_index(cls, dict_x, symbols: Symbols):
#         x_index_list = list()
#         max_vallen = 0

#         for i, (name, (_, bounds)) in enumerate(dict_x.items()):
#             # '//' is a comment format in Rust lang.
#             index = symbols.member[name][1]
#             x_index_list.append(f"{index},***space***// x[{i}] {name} (= p[{index}])\n")
#             vallen = len(str(index))
#             max_vallen = vallen if max_vallen < vallen else max_vallen

#         x_index_list = replace_space(x_index_list, ",", max_vallen)
#         return "".join(x_index_list)

#     @classmethod
#     def arrange_x_bounds(cls, dict_x, symbols: Symbols):
#         x_bounds_list = list()
#         max_vallen = 0

#         for i, (name, (_, bounds)) in enumerate(dict_x.items()):
#             # '//' is a comment format in Rust lang.
#             x_bounds_list.append(
#                 ""
#                 if bounds is None
#                 else f"{bounds},***space***// x[{i}] {name} (= p[{symbols.member[name][1]}])\n"
#             )
#             vallen = len(str(bounds))
#             max_vallen = vallen if max_vallen < vallen else max_vallen

#         if len(x_bounds_list) == 0:
#             str_x_bounds = "    let x_bounds = None;\n"
#         else:
#             x_bounds_list = replace_space(x_bounds_list, ",", max_vallen)
#             str_x_bounds = "".join(x_bounds_list)

#         return str_x_bounds

#     @classmethod
#     def collect_optimizer(cls, optimizer: Optimizer):
#         """
#         optimizer: Optimizer or List[Optimizer]
#             .options: Dict[str, value] or List[Dict[str, value]]
#         """
#         if not isinstance(optimizer, Optimizer):
#             raise TypeError(f"invalid type: {type(optimizer)}")
#         if optimizer.methods is None:
#             raise ValueError("designate optimization method")

#         optmethods = list()
#         optmethods_options = list()

#         for method in optimizer.methods:
#             optmethods.append(method.name)
#             if method.is_default:
#                 optmethods_options.append("default")
#             else:
#                 options = list()
#                 for key, value in method.options.items():
#                     if isinstance(value, bool):
#                         value = str(value).lower()
#                     options.append(key + ": " + str(value) + ",\n")
#                 optmethods_options.append("".join(options))
#         return optmethods, optmethods_options

#     @classmethod
#     def collect_obs(cls, obs: Obs):
#         if obs.data is None:
#             raise ValueError

#         obs_lines = list()
#         yname = ""
#         max_datalen = 0
#         for i, data in enumerate(obs.data):
#             if yname != data[0]:
#                 obs_lines.append(f"// {data[0]}\n")
#                 yname = data[0]

#             obs_line = (
#                 "("
#                 + str(data[5])
#                 + ", "
#                 + str(data[1])
#                 + ", "
#                 + str(data[2])
#                 + ", "
#                 + str(data[3])
#                 + ", "
#                 + str(data[4])
#                 + ")"
#             )
#             obs_lines.append(obs_line + ",***space***// d[" + str(i) + "]\n")
#             datalen = len(obs_line)
#             max_datalen = datalen if max_datalen < datalen else max_datalen

#         obs_lines = replace_space(obs_lines, "),", max_datalen)

#         return "".join(obs_lines)

#     @classmethod
#     def run(
#         cls,
#         model: BaseModel,
#         symbols: Symbols,
#         simulator: Simulator,
#         optimizer: Optimizer,
#         data: Obs,
#     ):
#         source = Source()
#         source = cls._common_with_inherited(
#             source, model, symbols, simulator, optimizer
#         )
#         source.lines["obs"] = cls.collect_obs(data)
#         return source
