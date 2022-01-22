HEADER = """fn main() {"""
FOOTER = """}\n"""

SIM_BODY = """
  let model = Model::new();

  let st_options = StepOptions::Dopri45 {
    h0: 1e-3,
    abstol: 1e-6,
    reltol: 1e-6,
    hmin: 1e-6,
    hmax: 1e-3,
  };
  let stepper = Stepper::Dopri45(st_options);
  let simulator = Simulator::new(model, stepper);

  let sampling_time = sampling_time();
  let simres = simulator.run(&sampling_time);
  simres.save("./res/");
"""

OPT_BODY = """
  let model = Model::new();
  let st_options = StepOptions::Dopri45 {
    h0: 1e-4,
    abstol: 1e-6,
    reltol: 1e-6,
    hmin: 1e-6,
    hmax: 1e-2,
  };
  let stepper = Stepper::Dopri45(st_options);
  let simulator = Simulator::new(model, stepper);

  let data = Data::new(obs());
  let mut objective = Objective::new(simulator, data);

  let ga_options = OptOptions::GeneticAlgorithm {
    max_gen: 10,
    n_pop: 50,
    mutation_rate: 0.5,
    verbose: true,
  };
  let optimizer = Optimizer::GeneticAlgorithm(ga_options);
  let optres = optimizer.run(&mut objective);
  objective.setx(&optres.x);

  let nm_options = OptOptions::NelderMead {
    max_iter: 0,
    adaptive: true,
    x_abstol: 1e-6,
    f_abstol: 1e-6,
    verbose: true,
  };
  let optimizer = Optimizer::NelderMead(nm_options);
  let optres = optimizer.run(&mut objective);
  optres.save("./res/");
"""
