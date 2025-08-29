import docker
import tarfile
import io
from .tools import Tool

class Container(Tool):
    def __init__(self, name=None, verbose=False):
        self.verbose = verbose
        self.client = docker.from_env()
        self.name = "run_command"
        if name is None:
            self.container = self.client.containers.run("ubuntu", auto_remove=True, detach=True, stdin_open=True)
        else:
            try:
                self.container = self.client.containers.get(name)
                self.container.restart()
            except docker.errors.NotFound:
                self.container = self.client.containers.run("ubuntu", auto_remove=False, detach=True, stdin_open=True, name=name)
                self._initial_installs()

    def _initial_installs(self):
        pass

    def __call__(self, cmd):
        cmd = f'/bin/bash -c "{cmd}"'
        return self.container.exec_run(cmd).output.decode()

    def __del__(self):
        try:
            self.container.stop()
        except:
            if self.verbose:
                print("Containers might not be cleaned up properly.")

    def remove(self):
        self.container.remove()

    def dict(self):
        return {
                "name" : "run_command",
                "description" : "Runs a single command in the command line, and returns its output. The system available is an Ubuntu docker container.",
                "parameters" : {
                    "type" : "object",
                    "properties" : {
                        "cmd" : {"type" : "string", "description" : "The command to run, including any arguments,"}},
                    "required" : ["cmd"],
                    }
                }





class PythonToolKit(Container):
    def __init__(self):
        super().__init__(name="dockerpy")
        self.censored_words = [
                "sys",
                "subprocess",
                "exec",
                "eval",
                "compile"]

    def _initial_installs(self):
        initial_install_script = """
        apt-get update
        apt-get install -y python3 python3-pip python3-venv git
        python3 -m venv .venv
        .venv/bin/pip install --upgrade pip
        .venv/bin/pip install numpy scipy matplotlib bqskit qiskit qsearch pytest
        """

        for line in initial_install_script.split("\n"):
            if line.isspace() or line == "":
                continue
            self(line)

    def sanitize_code(self, code):
        for word in self.censored_words:
            if word in code:
                return False
        return True

    def write_file(self, filename, contents):
        if not (self.sanitize_code(contents) and self.sanitize_code(filename)):
            return "The contents of the file failed security sanitization. File creation failed."
        with io.BytesIO() as f:
            with tarfile.open(fileobj=f, mode='w') as tar:
                encoded = contents.encode('utf-8')
                info = tarfile.TarInfo(filename)
                info.size = len(encoded)
                with io.BytesIO(encoded) as data:
                    tar.addfile(info, data)
            self.container.put_archive('.', f.getbuffer())
        return f"Successfully wrote to {filename}"

    def read_file(self, filename):
        return self(f"cat {filename}")

    def delete_file(self, filename):
        self(f"rm {filename}")
        return f"Deleted {filename}"

    def run_code(self, filename):
        return self(f".venv/bin/python3 {filename}")


    def get_tools(self):
        @Tool
        def write_file(filename: str, contents: str):
            """
            Creates a file with the given filename and contents.

            :filename: The name of the file to write.
            :contents: The contents of the file.
            """
            return self.write_file(filename, contents)

        @Tool
        def read_file(filename: str):
            """
            Reads and returns the contents of the file with the given filename, or returns an error message if the file does not exist.

            :filename: The name of the file to read.
            """
            return self.read_file(filename)

        @Tool
        def run_code(filename: str):
            """
            Runs the given file using python3, and returns the output.

            :filename: The name of the file to run.
            """
            return self.run_code(filename)

        return (write_file, read_file, run_code)
