CONST = """
const LEN_Y: usize = 4;
const LEN_P: usize = 11;
const LEN_B: usize = 2;

"""

STRUCT = """
#[allow(dead_code)]
pub struct Model {
  p: [f64; LEN_P],
}

"""

NEW_HEADER = """#[allow(dead_code)]
impl SimModelTrait<LEN_Y, LEN_P, LEN_B> for Model {
  fn new() -> Self {
    let p = [
"""

NEW_BODY = """      0.2,
      0.05,
"""

NEW_FOOTER = """    ];

    Self { p }
  }

"""

ODE_HEADER = """  #[allow(unused_variables)]
  fn ode(&self, t: &f64, y: &[f64; LEN_Y], deriv_y: &mut [f64; LEN_Y]) {
"""

ODE_FOOTER = """  }

"""


REC_HEADER = """  #[allow(unused_variables)]
  fn rec(&self, t: &f64, y: &[f64; LEN_Y], delta_y: &mut [f64; LEN_Y], act: &[bool; LEN_B]) {
"""

REC_FOOTER = """  }

"""
