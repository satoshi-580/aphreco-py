# =======================
# Import
# =======================
APHRECO_PRELUDE = """use aphreco::prelude::*;\n"""


# =======================
# Main
# =======================
# open main
OPEN_MAIN = """fn main() {
"""

# let model
LET_MODEL = """  let model = Model::new();

"""

# let simulator (stepper_options > stepper > simulator)
LET_STEP_OPTIONS_DEFAULT = """  let step_options = StepOptions::Default;
"""
LET_STEP_OPTIONS = """  let step_options = StepOptions::***method*** {
***options***  };
"""
LET_STEPPER = """  let stepper = Stepper::***method***(step_options);
"""


def _let_stepper(method: str, options: str):
    if options == "default":
        str_options = LET_STEP_OPTIONS_DEFAULT
    else:
        str_options = LET_STEP_OPTIONS
        str_options = str_options.replace("***method***", method)
        indent = " " * 4
        option_lines = list()
        for option in options.splitlines():
            option_lines.append(indent + option + "\n")
        str_options = str_options.replace("***options***", "".join(option_lines))

    str_stepper = LET_STEPPER.replace("***method***", method)
    return [str_options + str_stepper]


LET_SIMULATOR = """  let simulator = Simulator::new(model, stepper);

"""

# sampling time
LET_SMPTIME = """  let smptime = smptime();
"""

# run simulator
RUN_SIMULATOR = """  let simres = simulator.run(&smptime);
"""

# save simres
def _save_simres(dirpath: str):
    return f"""  simres.save("./res/{dirpath}/");
"""


# data
LET_DATA = """  let data = Data::new(obs());
"""

# objective
LET_OBJECTIVE = """  let mut objective = Objective::new(simulator, data);
"""

# let optimizer (optimizer_options > optimizer)
LET_OPTIMIZER_OPTIONS_DEFAULT = """  let opt_options = OptOptions::Default;
"""
LET_OPTIMIZER_OPTIONS = """  let opt_options = OptOptions::***method*** {
***options***  };
"""
LET_OPTIMIZER = """  let optimizer = Optimizer::***method***(opt_options);
"""


def _let_optimizer(method: str, options: str):
    if options == "default":
        str_options = LET_OPTIMIZER_OPTIONS_DEFAULT
    else:
        str_options = LET_OPTIMIZER_OPTIONS
        str_options = str_options.replace("***method***", method)
        indent = " " * 4
        option_lines = list()
        for option in options.splitlines():
            option_lines.append(indent + option + "\n")
        str_options = str_options.replace("***options***", "".join(option_lines))

    str_stepper = LET_OPTIMIZER.replace("***method***", method)
    return [str_options + str_stepper]


# run optimizer
RUN_OPTIMIZER = """  let optres = optimizer.run(&mut objective);
"""

# save optres
def _save_optres(dirpath: str):
    return f"""  optres.save("./res/{dirpath}/");
"""


# close main function
CLOSE_MAIN = """}
"""


# =======================
# Constants
# =======================
def _const_param_length(var: str, lines: str):
    length = lines.count("\n")
    return f"const LEN_{var}: usize = {length};\n"


# =======================
# Model
# =======================
# define struct
STRUCT = """
#[allow(dead_code)]
#[derive(Clone)]
pub struct Model {
  p: [f64; LEN_P],
}

"""

# =======================
# open SimTrait
OPEN_SIMTRAIT = """#[allow(dead_code)]
impl SimModelTrait<LEN_Y, LEN_P, LEN_B> for Model {
"""

# =======================
# fn new() in SimTrait
OPEN_NEW = """  fn new() -> Self {
"""
OPEN_P = """    let p = [
"""
CLOSE_P = """    ];
"""
CLOSE_NEW = """    Self { p }
  }
"""


def _fn_new(lines: str):
    header = OPEN_NEW + OPEN_P
    body = ""
    indent = " " * 6
    for line in lines.splitlines():
        body += indent + line + "\n"
    footer = CLOSE_P + CLOSE_NEW
    return header + body + footer


# =======================
# fn init() in SimTrait
OPEN_INIT = """  fn init(&self) -> (f64, [f64; LEN_Y]) {
"""
CLOSE_INIT = """    ];
    (t0, y0)
  }
"""


def _fn_init(str_time: str, y_lines: str):
    header = OPEN_INIT
    body = ""
    body += " " * 4 + "let t0 = " + str_time + ";\n"
    body += " " * 4 + "let y0 = [\n"
    indent = " " * 6
    for line in y_lines.splitlines():
        body += indent + line + "\n"
    footer = CLOSE_INIT
    return header + body + footer


# =======================
# fn ode() in SimTrait
OPEN_ODE = """  #[allow(unused_variables)]
  fn ode(&self, t: &f64, y: &[f64; LEN_Y], deriv_y: &mut [f64; LEN_Y]) {
"""
CLOSE_ODE = """  }
"""


def _fn_ode(lines: str):
    header = OPEN_ODE
    indent = " " * 4
    body = ""
    for line in lines.splitlines():
        body += indent + line + ";\n"
    footer = CLOSE_ODE
    return header + body + footer


# =======================
# fn rec() in SimTrait
OPEN_REC = """  #[allow(unused_variables)]
  fn rec(&self, t: &f64, y: &[f64; LEN_Y], delta_y: &mut [f64; LEN_Y], act: &[bool; LEN_B]) {
"""
CLOSE_REC = """  }
"""


def _fn_rec(lines: str):
    header = OPEN_REC
    act_indent = " " * 4
    delta_indent = " " * 6
    body = ""
    beat_id = 0
    for line in lines.splitlines():
        if line.startswith("==="):
            if beat_id > 0:
                body += act_indent + "}\n"
            body += act_indent + "if act[" + str(beat_id) + "] {\n"
            beat_id += 1
        else:
            body += delta_indent + line + ";\n"
    body += act_indent + "}\n"
    footer = CLOSE_REC
    return header + body + footer


# =======================
# fn cond() in SimTrait
OPEN_COND = """  #[allow(unused_variables)]
  fn cond(
    &self,
    dec_t: &Decimal,
    act: &mut [bool; LEN_B],
    next_t: &[Decimal; LEN_B],
    y: &[f64; LEN_Y],
  ) {
"""
CLOSE_COND = """  }
"""


def _fn_cond(lines: str):
    header = OPEN_COND
    indent = " " * 4
    body = ""
    for line in lines.splitlines():
        body += indent + line + ";\n"
    footer = CLOSE_COND
    return header + body + footer


# =======================
# fn beat() in SimTrait
OPEN_BEAT = """  #[allow(unused_variables)]
  fn beat(&self, t: &f64, y: &[f64; LEN_Y]) -> [[Decimal; 3]; LEN_B] {
"""
CLOSE_BEAT = """  }
"""


def _fn_beat(lines: str):
    header = OPEN_BEAT
    indent = " " * 6
    body = " " * 4 + "[\n"
    for line in lines.splitlines():
        body += indent + line + "\n"
    body += " " * 4 + "]\n"
    footer = CLOSE_BEAT
    return header + body + footer


# =======================
# fn cre() in SimTrait
OPEN_CRE = """  #[allow(unused_variables)]
  fn cre(&self, t: &f64, y: &mut [f64; LEN_Y]) {
"""
CLOSE_CRE = """  }
"""


def _fn_cre(lines: str):
    header = OPEN_CRE
    indent = " " * 4
    body = ""
    for line in lines.splitlines():
        body += indent + line + ";\n"
    footer = CLOSE_CRE
    return header + body + footer


# =======================
# close SimTrait
CLOSE_SIMTRAIT = """}

"""


# =======================
# open OptTrait
OPEN_OPTTRAIT = """#[allow(dead_code)]
impl OptModelTrait<LEN_Y, LEN_P, LEN_B, LEN_X> for Model {
"""

# =======================
# fn getx() in OptTrait
GETX_HEADER = """  fn getx(&self) -> (Vec<usize>, Option<Vec<(f64, f64)>>) {
"""
GETX_FOOTER = """    (x_index, x_bounds)
  }
"""


def _fn_getx(x_index_lines: str, x_bounds_lines: str):
    header = GETX_HEADER

    indent = " " * 6

    x_index = "    let x_index = vec![\n"
    for line in x_index_lines.splitlines():
        x_index += indent + line + "\n"
    x_index += "    ];\n"

    if x_bounds_lines == "None":
        x_bounds = "    let x_bounds = None;\n"
    else:
        x_bounds = "    let x_bounds = Some(vec![\n"
        for line in x_bounds_lines.splitlines():
            x_bounds += indent + line + "\n"
        x_bounds += "    ]);\n"

    footer = GETX_FOOTER
    return header + x_index + x_bounds + footer


# =======================
# fn getp() in OptTrait
FN_GETP = """  fn getp(&self) -> &[f64; LEN_P] {
    &self.p
  }
"""

# =======================
# fn setp() in OptTrait
FN_SETP = """  fn setp(&mut self, index: usize, value: f64) {
    self.p[index] = value;
  }
"""


# =======================
# close OptTrait
CLOSE_OPTTRAIT = """}

"""


# =======================
# Sampling Time in Simulation
# =======================
OPEN_SMPTIME = """fn smptime() -> Vec<f64> {
"""
CLOSE_SMPTIME = """}

"""


def _fn_smptime(smptime_lines: str):
    header = OPEN_SMPTIME
    body = "".join(["""  vec![""", smptime_lines, """]\n"""])
    footer = CLOSE_SMPTIME
    return header + body + footer


# =======================
# Observed Data in Optimization
# =======================
OBS_HEADER = """#[allow(dead_code)]
fn obs() -> Vec<(usize, f64, f64, Option<f64>, Option<f64>)> {
  vec![
"""
OBS_FOOTER = """  ]
}

"""


def _fn_obs(data_lines: str):
    header = OBS_HEADER
    indent = " " * 4
    body = ""
    for line in data_lines.splitlines():
        body += indent + line + "\n"
    footer = OBS_FOOTER
    return header + body + footer
