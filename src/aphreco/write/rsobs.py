OBS_HEADER = """#[allow(dead_code)]
fn obs() -> Vec<(usize, f64, f64, Option<f64>, Option<f64>)> {
  vec![
"""
OBS_FOOTER = """  ]
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
