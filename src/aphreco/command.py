import shlex
import subprocess


class RustCompilationError(Exception):
    pass


class Command:
    def __init__(self):
        self.sim_compile = "cargo build --release "
        self.sim_run = "cargo run --release "

    def compile(self, filename):
        success = True
        with subprocess.Popen(
            shlex.split(self.sim_compile + filename),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as p:
            while True:
                line = p.stdout.readline()
                if "Error:" in line:
                    x = line.find("Error:")
                    print(line[:x])
                    success = False
                if not line and p.poll() is not None:
                    break
        if not success:
            raise RustCompilationError("rust compilation failed.")
