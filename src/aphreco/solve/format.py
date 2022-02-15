from collections import OrderedDict
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Union

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


def range_f2s(start: float, stop: float, step: float):
    dec_start = Decimal(str(start))
    dec_stop = Decimal(str(stop))
    dec_step = Decimal(str(step))

    for i in range(int((dec_stop - dec_start) / dec_step)):
        yield str(dec_start + i * dec_step)


class BaseFormatter:
    def __init__(self, simplify_eq=False):
        self.simplify_eq = simplify_eq

    @property
    def simplify_eq(self):
        return self._simplify_eq

    @simplify_eq.setter
    def simplify_eq(self, simplify_eq):
        self._simplify_eq = simplify_eq


class SimFormatter(BaseFormatter):
    """"""

    def format_model_info(self, dicts: Tuple) -> Dict[str, str]:
        names_dict, vals_dict, terms_dict = dicts
        lines = OrderedDict()
        # Format collected dicts into lines
        lines["t"] = self.line_t(vals_dict)
        lines["y"] = self.line_y(names_dict, vals_dict)
        lines["p"] = self.line_p(names_dict, vals_dict)

        lines["ode"] = self.arrange_ode(terms_dict["ode"])
        str_rec, str_cond, str_beat = self.arrange_rec(terms_dict["rec"])
        lines["rec"] = str_rec
        lines["cond"] = str_cond
        lines["beat"] = str_beat
        lines["cre"] = self.arrange_cre(terms_dict["cre"])

        return lines

    def line_t(self, vals_dict: Dict[str, float]) -> str:
        initime = "initime"
        if initime not in vals_dict.keys():
            raise KeyError(f"Variable '{initime}' is not in a model.")
        return str(vals_dict[initime])

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

    def format_simulator_info(self, lines, simulator):
        """
        Returns:
            Tuple[str, str]
        """
        if simulator.stepper.is_default:
            stepper_options = "default"
        else:
            stepper_options = ""
            for key, value in simulator.stepper.options.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                stepper_options += key + ": " + str(value) + ",\n"

        lines["stepper"] = simulator.stepper.name
        lines["stepper_options"] = stepper_options
        return lines

    def format_smptime_info(
        self,
        lines: Dict[str, str],
        smptime: Union[Tuple[float, float, float], List[float]],
    ):
        """create lines for sampling times, which is unique to simulation."""

        # smptime
        if isinstance(smptime, tuple) and len(smptime) == 3:
            start = float(smptime[0])
            stop = float(smptime[1])
            step = float(smptime[2])
            smptime_list = range_f2s(start, stop, step)
        elif isinstance(smptime, list):
            smptime_list = [str(float(t)) for t in smptime]
        else:
            try:
                smptime_list = [str(t) for t in smptime]
            except:
                raise ValueError
        lines["smptime"] = ", ".join(smptime_list)

        return lines


class OptFormatter(SimFormatter):
    def format_model_info(self, dicts: Tuple) -> Dict[str, str]:
        names_dict, vals_dict, terms_dict, unks_dict = dicts
        lines = super().format_model_info((names_dict, vals_dict, terms_dict))
        lines["x_index"] = self._arrange_x_index(unks_dict)
        lines["x_bounds"] = self._arrange_x_bounds(unks_dict)
        return lines

    def _arrange_x_index(
        self,
        unks_dict: Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]],
    ) -> str:
        lines = list()
        max_vallen = 0
        for i, (name, (_, p_index, _)) in enumerate(unks_dict.items()):
            lines.append(f"{p_index},***space***// p[index] of x[{i}] {name}\n")
            vallen = len(str(p_index))
            max_vallen = vallen if max_vallen < vallen else max_vallen
        lines = _replace_space(lines, ",", max_vallen)
        return "".join(lines)

    def _arrange_x_bounds(
        self,
        unks_dict: Dict[str, Tuple[float, int, Optional[Tuple[float, float]]]],
    ) -> str:
        lines = list()
        max_vallen = 0
        for i, (name, (_, p_index, bounds)) in enumerate(unks_dict.items()):
            if bounds is not None:
                lines.append(f"{bounds},***space***// x[{i}] {name} (= p[{p_index}])\n")
                vallen = len(str(bounds))
                max_vallen = vallen if max_vallen < vallen else max_vallen

        if len(lines) == 0:
            return "None"
        else:
            lines = _replace_space(lines, ",", max_vallen)
            return "".join(lines)

    def format_optimizer_info(self, lines, optimizer):
        """
        optimizer: Optimizer
            .options: Dict[str, value]
        """
        lines["optimizer"] = optimizer.method.name

        if optimizer.method.is_default:
            str_opt_options = "default"
        else:
            options = list()
            for key, value in optimizer.method.options.items():
                if isinstance(value, bool):
                    value = str(value).lower()
                options.append(key + ": " + str(value) + ",\n")
            str_opt_options = "".join(options)
        lines["optimizer_options"] = str_opt_options

        return lines

    def format_obs_info(self, lines, data):
        """formats observation data."""
        obs_lines = list()
        yname = ""
        max_datalen = 0
        for i, record in enumerate(data.table):
            if yname != record[0]:
                obs_lines.append(f"// {record[0]}\n")
                yname = record[0]

            obs_line = (
                "("
                + str(record[5])
                + ", "
                + str(record[1])
                + ", "
                + str(record[2])
                + ", "
                + str(record[3])
                + ", "
                + str(record[4])
                + ")"
            )
            obs_lines.append(obs_line + ",***space***// d[" + str(i) + "]\n")
            datalen = len(obs_line)
            max_datalen = datalen if max_datalen < datalen else max_datalen

        obs_lines = _replace_space(obs_lines, "),", max_datalen)

        lines["obs"] = "".join(obs_lines)
        return lines
