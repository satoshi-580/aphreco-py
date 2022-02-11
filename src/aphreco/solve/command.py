import shlex
import subprocess


class RustError(Exception):
    pass


class Command:
    def run(self, cmd):
        success = True
        with subprocess.Popen(
            shlex.split(cmd),
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
                if (not line) and (p.poll() is not None):
                    break

        if not success:
            raise RustError("rust compilation/execution failed.")

    def compile(self):
        cmd_compile = "cargo run"
        self.run(cmd_compile)

    def release(self):
        cmd_release = "cargo build --release && cargo run --release"
        self.run(cmd_release)
