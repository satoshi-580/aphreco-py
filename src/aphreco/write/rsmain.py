HEADER = """fn main() {"""

SIM_BODY = """
  let model = Model::new();
  let simulator = Simulator::new(model, Stepper::Dopri45);

  let sampling_time = sampling_time();
  let simres = simulator.run(&sampling_time);
  simres.save("/");
"""

OPT_BODY = """
  let model = Model::new();
  let simulator = Simulator::new(model, Stepper::Dopri45);

  let data = Data::new(observation());
  let mut objective = Objective::new(simulator, data);

  let optimizer = Optimizer::GeneticAlgorithm;
  let optres = optimizer.run(&mut objective);
  objective.setx(&optres.x);

  let optimizer = Optimizer::NelderMead;
  let optres = optimizer.run(&mut objective);
  optres.save("./");
"""


FOOTER = """}\n"""
