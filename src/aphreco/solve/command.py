import shlex
import subprocess


class RustError(Exception):
    pass


class Command:
    def exe(self, cmd):
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
                if "thread 'main' panicked" in line:
                    x = line.find("Error:")
                    success = False

                if (not line) and (p.poll() is not None):
                    break

        if not success:
            raise RustError("rust execution failed.")

    def compile(self):
        self.exe("cargo run")

    def release(self):
        self.exe("cargo build --release")
        self.exe("cargo run --release")
