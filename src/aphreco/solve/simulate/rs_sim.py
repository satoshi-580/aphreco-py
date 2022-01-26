def write_const(len_y: int, len_p: int, len_b: int):
    str_const = "\n"
    str_const += f"const LEN_Y: usize = {len_y};\n"
    str_const += f"const LEN_P: usize = {len_p};\n"
    str_const += f"const LEN_B: usize = {len_b};\n"
    str_const += "\n"

    return str_const


IMPL_SIMTRAIT = """#[allow(dead_code)]
impl SimModelTrait<LEN_Y, LEN_P, LEN_B> for Model {
"""
END_IMPL_SIMTRAIT = """}\n\n"""

NEW_HEADER = """  fn new() -> Self {
    let p = [
"""
NEW_FOOTER = """    ];

    Self { p }
  }

"""


def write_fn_new(picked_p: str):
    new_header = NEW_HEADER

    new_body = ""
    indent = " " * 6
    for line in picked_p.splitlines():
        new_body += indent + line + "\n"

    new_footer = NEW_FOOTER
    return new_header + new_body + new_footer


INIT_HEADER = """  fn init(&self) -> (f64, [f64; LEN_Y]) {
"""
INIT_FOOTER = """    ];

    (t0, y0)
  }

"""


def write_fn_init(picked_t: str, picked_y: str):
    header = INIT_HEADER

    body = ""
    body += " " * 4 + "let t0 = " + picked_t + ";\n"
    body += " " * 4 + "let y0 = [\n"
    indent = " " * 6
    for line in picked_y.splitlines():
        body += indent + line + "\n"

    footer = INIT_FOOTER
    return header + body + footer


ODE_HEADER = """  #[allow(unused_variables)]
  fn ode(&self, t: &f64, y: &[f64; LEN_Y], deriv_y: &mut [f64; LEN_Y]) {
"""
ODE_FOOTER = """  }

"""


def write_fn_ode(picked_ode: str):
    ode_header = ODE_HEADER

    indent = " " * 4
    ode_body = ""
    for line in picked_ode.splitlines():
        ode_body += indent + line + ";\n"

    ode_footer = ODE_FOOTER
    return ode_header + ode_body + ode_footer


REC_HEADER = """  #[allow(unused_variables)]
  fn rec(&self, t: &f64, y: &[f64; LEN_Y], delta_y: &mut [f64; LEN_Y], act: &[bool; LEN_B]) {
"""
REC_FOOTER = """  }

"""


def write_fn_rec(picked_rec: str):
    rec_header = REC_HEADER

    act_indent = " " * 4
    delta_indent = " " * 6
    rec_body = ""
    beat_id = 0
    for line in picked_rec.splitlines():
        if line.startswith("==="):
            if beat_id > 0:
                rec_body += act_indent + "}\n"
            rec_body += act_indent + "if act[" + str(beat_id) + "] {\n"
        else:
            rec_body += delta_indent + line + ";\n"
    rec_body += act_indent + "}\n"

    rec_footer = REC_FOOTER
    return rec_header + rec_body + rec_footer


COND_HEADER = """  #[allow(unused_variables)]
  fn cond(
    &self,
    dec_t: &Decimal,
    act: &mut [bool; LEN_B],
    next_t: &[Decimal; LEN_B],
    y: &[f64; LEN_Y],
  ) {
"""
COND_FOOTER = """  }

"""


def write_fn_cond(picked_cond_reg: str):
    header = COND_HEADER

    indent = " " * 4
    body = ""
    for line in picked_cond_reg.splitlines():
        body += indent + line + ";\n"

    footer = COND_FOOTER
    return header + body + footer


BEAT_HEADER = """  #[allow(unused_variables)]
  fn beat(&self,t: &f64, y: &[f64; LEN_Y]) -> [[Decimal; 3]; LEN_B] {
"""
BEAT_FOOTER = """  }

"""


def write_fn_beat(picked_beat: str):
    header = BEAT_HEADER

    indent = " " * 6
    body = " " * 4 + "[\n"
    for line in picked_beat.splitlines():
        body += indent + line + "\n"
    body += " " * 4 + "]\n"

    footer = BEAT_FOOTER
    return header + body + footer


CRE_HEADER = """  #[allow(unused_variables)]
  fn cre(&self, t: &f64, y: &mut [f64; LEN_Y]) {
"""
CRE_FOOTER = """  }

"""


def write_fn_cre(picked_cre: str):
    cre_header = CRE_HEADER

    indent = " " * 4
    cre_body = ""
    for line in picked_cre.splitlines():
        cre_body += indent + line + ";\n"

    cre_footer = ODE_FOOTER
    return cre_header + cre_body + cre_footer
