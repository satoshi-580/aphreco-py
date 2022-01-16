MAIN_HEADER = """use aphreco::prelude::*;

fn main() {"""

MAIN_BODY = """
  let model = Model::new();
  let simulator = Simulator::new(model, Stepper::Dopri45);
  let sampling_time = sampling_time();
  let simres = simulator.run(&sampling_time);
  simres.save("/");
"""

MAIN_FOOTER = """}\n"""
