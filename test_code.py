from ollama import Chat
from dockerpy import PythonToolKit


toolkit = PythonToolKit()
#toolkit.install_python()
chat = Chat("qwen3:32b")
for tool in toolkit.get_tools():
    chat.add_tool(tool)

chat.prompt("Please generate a number between 1 and 100. Use python to help you choose a number fairly.")
chat.print()
