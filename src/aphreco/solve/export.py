from pathlib import Path

CARGO_TOML = """[package]
name = "aphrecode"
version = "0.1.0"
edition = "2021"

[dependencies]
aphreco = "0.1.*"
"""


def _save_content_as(filepath, content):
    with open(filepath, "w") as f:
        f.write(content)


class Exporter:
    def __init__(self, path=Path.cwd()):
        if not isinstance(path, Path):
            path = Path(path)

        if not path.exists():
            raise ValueError(f"directory not found.")

        self.path = path

    def _mkdir_if_not_exists(self, dirname: str):
        path_src = self.path / dirname
        if not path_src.exists():
            path_src.mkdir()

    def _mk_cargo_toml_if_not_exists(self):
        # create Cargo.toml
        path_cargo_toml = self.path / "Cargo.toml"
        if not path_cargo_toml.exists():
            _save_content_as(path_cargo_toml, CARGO_TOML)

    def check_env(self):
        self._mk_cargo_toml_if_not_exists()
        self._mkdir_if_not_exists("src")
        self._mkdir_if_not_exists("res")

    def create_main(self, codes):
        # save the source code as main.rs
        path_main = self.path / "src" / "main.rs"
        _save_content_as(path_main, codes)
