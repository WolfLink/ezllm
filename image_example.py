# How to get started quickly:
from ezllm import Chat

chat = Chat()
response = chat.prompt("Hello World") # The response is returned as a string
print(response)

# You can print the whole conversation in a nicely formatted way
chat.print()

# You can choose a specific model (the default is qwen3:latest)
chat = Chat("qwen3:1.7b")



# You can easily add python functions as tools for the llm to use
from ezllm import Tool

# Adding type annotations and a docstring is not necessary, but it will help your LLM understand how to use the tool better.
@Tool
def divide(n: int, d: int) -> float:
    """
    This function divides two numbers and returns the result as a floating point number.

    :n: The numerator.
    :d: The divisor.
    """
    return n / d

chat.add_tools(divide)
result = chat.prompt("Use your tool to divie 42 by 9")
chat.print()


# You can also add MCPs as tools
from ezllm import MCPClient

client = MCPClient("https://remote.mcpservers.org/fetch/mcp")
chat.add_tools(client)
result = chat.prompt("How can I easily use local llms using ezllm? Please use the fetch tool to look at the README from that github repo and explain it to me. Use this link: https://raw.githubusercontent.com/WolfLink/ezllm/refs/heads/main/README.md")
print(result)

# There are other options for adding MCPs
# This support is built on top of FastMCP, so see https://gofastmcp.com/clients/client for documentation of all the ways you can provide an MCP.


# You can export a chat through as json. This includes the chat history, as well as information such as what model you were using.
# Tools are not saved in this way.
chatdata = chat.to_json()

# This creates a new Chat object from the data. The model and messages will be loaded from the chat data, but tools are not saved and must be re-added.
chat = Chat.from_json(chatdata)

# This loads the chat data into an existing Chat object. The model and messages will be loaded from the data, but the tools will not change. This is often faster because it won't restart the container, and is useful if you are using the same set of tools but want to load a different chat history.
chat.load_json(chatdata)
