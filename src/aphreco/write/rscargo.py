CARGO_TOML = """[package]
name = "aphreco"
version = "0.1.0"
edition = "2021"

[dependencies]
aphreco = "0.1.0"
"""


def create_toml(filepath):
    with open(filepath, "w") as f:
        f.write(CARGO_TOML)
