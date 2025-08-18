from ollama import Chat
from tools import Tool

code_manager = Chat(model="qwen3:32b")
code_writer = Chat(model="qwen3:32b")


def filter_code(text, code_type='python'):
    code = ""
    is_code = False
    for line in text.splitlines():
        if "```python" in line:
            is_code = True
        elif "```" in line:
            is_code = False
        elif is_code:
            code += f"{line}\n"
    return code

@Tool
def write_file(filename: str, contents: str):
    """
    Creates a file using the given filename and contents.

    :filename: The name of the file.
    :contents: The contents of the file, as plaintext.
    """
    with open(filename, "w") as f:
        f.write(contents)
    return f"File created: {filename}"

@Tool
def write_tests(prompt: str):
    """
    Writes units tests based on the given prompt.

    :prompt: A description of what the code should do.
    """
    code_writer.memory_wipe()
    code_writer.system("Your task is to write unit tests in Python. The user will give you a description of what the code must do, and you will write unit tests in pytest format based on that description.")
    with open("generated_tests.py", "w") as f:
        f.write(filter_code(code_writer.prompt(prompt)))
    return "Unit tests written to generated_tests.py"

@Tool
def write_code(prompt: str, unit_tests: str):
    """
    Writes code based on the given prompt that passes the unit tests in the given file.

    :prompt: A verbal description of what the code should do.
    :unit_tests: A pytest unit tests file that validates the code solution.
    """
    code_writer.memory_wipe()
    code_writer.system("Your task is to write Python code based on the user prompt. Your code will be evaluated against a suite of pytest unit tests. The unit tests are provided below for your reference.")
    with open("generated_tests.py", "r") as f:
        code_writer.system(f.read())
    result = code_writer.prompt(prompt)
    with open("generated_solution.py", "w") as f:
        f.write(filter_code(result))
    return "All unit tests passed!"

@Tool
def write_requirements(code: str):
    """
    Writes a requirements.txt for a given Python program.

    :code: The Python code for which a requirements.txt is needed.
    """
    code_writer.memory_wipe()
    code_writer.system("Your task is to take the Python code given by the user and generate the contents of a requirements.txt to import the required libraries for that Python code. As a reminder, a requirements.txt file contains each Python package that must be installed on a newline, with no comments or other text.")
    with open("generated_requirements.txt", "w") as f:
        f.write(code_writer.prompt(code))
    return "requirements.txt written."

@Tool
def auto_coder(prompt: str):
    """
    Writes code based on a detailed text-based description of what the code should do.

    :prompt: A detailed text-based description of what the code needs to do.
    """
    test_file = write_tests(prompt)
    write_code(prompt, test_file)
    write_requirements(prompt)
    return "The code has been written!"

code_manager.add_tool(auto_coder)
code_manager.system("If the user asks you to solve any scientific or mathematical problems, use your auto_coder tool to help you.")
#print(code_manager.prompt("How are you doing today?"))
print(code_manager.prompt("I am trying to compute the ground state energy of Hydrogen using a quantum computer. Can you help be with this task?"))
print("\n\n")
for message in code_manager.messages:
    print(message)

