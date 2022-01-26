SMP_TIME_HEADER = """fn smp_time() -> Vec<f64> {
  let mut vec_smp_t = Vec::new();
"""
SMP_TIME_FOOTER = """   vec_smp_t
}

"""


def str_fn_sampling_time(picked_smp_t: str):
    header = SMP_TIME_HEADER

    body = """   for i in 0..=5000 {
    vec_smp_t.push(i as f64 / 100.0);
  }
"""

    footer = SMP_TIME_FOOTER
    return header + body + footer
