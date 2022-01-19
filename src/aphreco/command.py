import shlex
import subprocess


class RustCompilationError(Exception):
    pass


class Command:
    def __init__(self):
        self.cargo_run = "cargo run"

    def compile(self):
        success = True
        with subprocess.Popen(
            shlex.split(self.cargo_run),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as p:
            while True:
                line = p.stdout.readline()
                print(line, end="")
                if "panic:" in line:
                    x = line.find("Error:")
                    print(line[:x])
                    success = False
                if not line and p.poll() is not None:
                    break
        if not success:
            raise RustCompilationError("rust compilation failed.")
