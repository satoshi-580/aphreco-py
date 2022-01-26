def write_const(len_x: int):
    str_const = "\n"
    str_const += f"const LEN_X: usize = {len_x};\n"
    str_const += "\n"

    return str_const


IMPL_OPTTRAIT = """#[allow(dead_code)]
impl OptModelTrait<LEN_Y, LEN_P, LEN_B, LEN_X> for Model {
"""
END_IMPL_OPTTRAIT = """}\n\n"""

GETX_HEADER = """  fn getx(&self) -> (Vec<usize>, Option<Vec<(f64, f64)>>) {
"""
GETX_FOOTER = """    (x_index, x_bounds)
  }

"""


def write_fn_getx(picked_x_index: str, picked_x_bounds: str):
    header = GETX_HEADER

    indent = " " * 6

    x_index = "    let x_index = vec![\n"
    for line in picked_x_index.splitlines():
        x_index += indent + line + "\n"
    x_index += "    ];\n"

    if picked_x_bounds == "    let x_bounds = None;\n":
        x_bounds = picked_x_bounds
    else:
        x_bounds = "    let x_bounds = Some(vec![\n"
        for line in picked_x_bounds.splitlines():
            x_bounds += indent + line + "\n"
        x_bounds += "    ]);\n"

    footer = GETX_FOOTER
    return header + x_index + x_bounds + footer


FN_GETP = """  fn getp(&self) -> &[f64; LEN_P] {
    &self.p
  }

"""
FN_SETP = """  fn setp(&mut self, index: usize, value: f64) {
    self.p[index] = value;
  }

"""
