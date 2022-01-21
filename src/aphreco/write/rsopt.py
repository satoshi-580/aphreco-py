def write_const(len_x: int):
    str_const = "\n"
    str_const += f"const LEN_X: usize = {len_x};\n"
    str_const += "\n"

    return str_const


IMPL_SIMTRAIT = """#[allow(dead_code)]
impl OptModelTrait<LEN_Y, LEN_P, LEN_B, LEN_X> for Model {
"""

GETX_HEADER = """  fn getx(&self) -> (Vec<usize), Option<Vec<(f64, f64)>>) {
"""
GETX_FOOTER = """    (x_index, x_bounds)
  }

"""


def write_fn_getx(picked_p: str):
    header = GETX_HEADER

    body = ""
    indent = " " * 6
    for line in picked_p.splitlines():
        body += indent + line + "\n"

    footer = GETX_FOOTER
    return header + body + footer


FN_GETP = """  fn getp(&self) -> &[f64; LEN_P] {
    &self.p
  }

"""
FN_SETP = """  fn setp(&mut self, index: usize, value: f64) {
    self.p[index] = value;
  }

"""


OBS_HEADER = """  #[allow(dead_code)]
fn observation() -> Vec<(usize, f64, f64, Option<f64>, Option<f64>)> {
  vec!["""
OBS_FOOTER = """    ]
  }

"""


def write_fn_obs(picked_data: str):
    header = OBS_HEADER

    indent = " " * 4
    body = ""
    for line in picked_data.splitlines():
        body += indent + line + "\n"

    footer = OBS_FOOTER
    return header + body + footer
