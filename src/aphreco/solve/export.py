from pathlib import Path


class Exporter:
    def __init__(self, path="."):
        self.path = path

    def check_env(self):
        return Path("./res").exists()

    def mkdir_res(self):
        pass

    def mk_cargo_toml(self):
        pass


#     def save(self, code: str):
#         path = Path.cwd()

#         # create Cargo.toml
#         path_cargo_toml = path / "Cargo.toml"
#         if not path_cargo_toml.exists():
#             rs_cargo.create_toml(path_cargo_toml)

#         # create src directory
#         path_src = path / "src"
#         if not path_src.exists():
#             path_src.mkdir()

#         # create res directory
#         path_res = path / "res"
#         if not path_res.exists():
#             path_res.mkdir()

#         # save the source code as main.rs
#         file_name = "main.rs"
#         with open(path_src / file_name, "w") as f:
#             f.write(code)

#         # save a backup file in res
#         str_now = datetime.now().strftime("%Y%m%d_%H%M%S")
#         file_name = "aphrecode_" + str_now + ".rs"
#         with open(path_res / file_name, "w") as f:
#             f.write(code)

#         return file_name
