import docker
from tools import Tool

class Container(Tool):
    def __init__(self, verbose=False):
        self.verbose = verbose
        self.client = docker.from_env()
        self.name = "run_command"
        self.container = self.client.containers.run("ubuntu", auto_remove=True, detach=True, stdin_open=True)

        initial_install_script = """
        apt-get update
        apt-get install -y python3 python3-pip
        """
        for line in initial_install_script.split("\n"):
            if line.isspace() or line == "":
                continue
            if verbose:
                print(self(line))
            else:
                self(line)

    def __call__(self, *args, **kwargs):
        return self.container.exec_run(*args, **kwargs).output.decode()

    def __del__(self):
        try:
            self.container.stop()
        except:
            if self.verbose:
                print("Containers might not be cleaned up properly.")

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
