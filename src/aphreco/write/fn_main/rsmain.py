from cgi import print_form
from typing import List

HEADER = """fn main() {
"""
FOOTER = """}\n"""

LET_MODEL = """  let model = Model::new();

"""

LET_STEP_OPTIONS = """  let step_options = StepOptions::***method*** {
    ***options***
  };
"""
LET_STEP_OPTIONS_DEFAULT = """  let step_options = StepOptions::Default;
"""
LET_STEPPER = """  let stepper = Stepper::***method***(step_options);
"""


def _write_let_stepper(method: str, options: str):
    if options == "default":
        str_options = LET_STEP_OPTIONS_DEFAULT
    else:
        str_options = LET_STEP_OPTIONS
        str_options = str_options.replace("***method***", method)
        str_options = str_options.replace("***options***", options)

    str_stepper = LET_STEPPER.replace("***method***", method)
    return str_options + str_stepper


LET_SIMULATOR = """  let simulator = Simulator::new(model, stepper);

"""

RUN_SIMULATOR = """  let sampling_time = sampling_time();
  let simres = simulator.run(&sampling_time);
"""
SAVE_SIMRES = """  simres.save("./res/");
"""

LET_DATA = """  let data = Data::new(obs());
"""
LET_OBJECTIVE = """  let mut objective = Objective::new(simulator, data);

"""

LET_OPTIMIZER_OPTIONS = """  let options = OptOptions::***method*** {
    ***options***
  };
"""
LET_OPTIMIZER_OPTIONS_DEFAULT = """  let options = OptOptions::Default;
"""
LET_OPTIMIZER = """  let optimizer = Optimizer::***method***(options);
"""
RUN_OPTIMIZER = """  let optres = optimizer.run(&mut objective);
"""
SET_X_TO_OBJECTIVE = """
  objective.setx(&optres.x);

"""
SAVE_OPTRES = """
  optres.save("./res/");
"""


def _write_let_optimizer(list_methods: List[str], list_options: List[str]):
    list_str_opts = list()
    n_opts = len(list_methods)
    for i, (method, options) in enumerate(zip(list_methods, list_options)):
        if options == "default":
            str_options = LET_OPTIMIZER_OPTIONS_DEFAULT
        else:
            str_options = LET_OPTIMIZER_OPTIONS
            str_options = str_options.replace("***method***", method)
            str_options = str_options.replace("***options***", options)

        str_optimizer = (LET_OPTIMIZER + RUN_OPTIMIZER).replace("***method***", method)

        # dealing after optimization
        # save optres if it is the last optimization process,
        # or use optimized x as the next if not last.
        if i == n_opts - 1:
            str_after = SAVE_OPTRES
        else:
            str_after = SET_X_TO_OBJECTIVE

        list_str_opts.append(str_options + str_optimizer + str_after)

    return list_str_opts
