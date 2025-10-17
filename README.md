# EZLLM

Start programming with locally hosted LLMs with only a few lines of code!

```python
from ezllm import Chat

chat = Chat()
response = chat.prompt("Hello World")
print(response)
```

EZLLM is designed for simplifying the process of incorporating LLMs into a programming project through automated prompting and tool usage, enabling LLMs to perform complex tasks on their own. EZLLM allows you to send message to and receive the output from LLMs, and provide them your Python code as tools, with only a few lines of code.

EZLLM is built on top of [Ollama](https://ollama.com/), which provides a free and open-source way to locally host many different LLMs. EZLLM runs Ollama inside a [Docker container](https://docs.docker.com/engine/install/). Python functions can be added directly as tools using `ezllm.Tool` but you can also add MCPs, with support built using [FastMCP](https://gofastmcp.com/getting-started/welcome).


# Installation
## Docker
This code is built around running Ollama in a docker container. To use it, you first need to setup Docker and add yourself to the docker group.

1. Install Docker: https://docs.docker.com/engine/install/
2. Add yourself to the docker group:
```bash
sudo usermod -aG docker $USER
```
3. Log out and log back in (or restart the computer).

## Nvidia Container Toolkit
If you have an Nvidia GPU that you would like to use for accelerating LLMs, you need to install the Nvidia Container Toolkit.

https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html

## EZLLM
Once you have installed the prerequisites, you can install ezllm with pip:
```bash
pip install git+https://github.com/WolfLink/ezllm.git
```


# Usage

## Chatting
Simply create a `Chat` object. You can send messages with `prompt` and receive the response as a string.
```python
from ezllm import Chat

chat = Chat()
response = chat.prompt("Hello World")
```
You can choose a specific model (the default is qwen3:latest).
```python
chat = Chat("qwen3:1.7b")
```
You can print a formatted chat log with `print`.
```python3
chat.print()
```


## Tools (Local and MCP)

You can easily add python functions as tools for the llm to use:
```python
from ezllm import Chat, Tool

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
```

You can also add MCPs as tools:
```python
from ezllm import Chat, MCPClient

client = MCPClient("https://remote.mcpservers.org/fetch/mcp")
chat.add_tools(client)
result = chat.prompt("How can I easily use local llms using https://github.com/WolfLink/ezllm ? Look at the README from that github and explain it to me.")
print(result)
```
There are other options for adding MCPs, such as using a passing in the JSON configuration for an MCP client as a string.
This support is built on top of FastMCP, so see https://gofastmcp.com/clients/client for documentation of all the ways you can provide an MCP.


## Saving and Loading a Chat History

You can export a chat through as json. This includes the chat history, as well as information such as what model you were using. Tools are not saved in this way.
```python
chatdata = chat.to_json()
```

You can create a new `Chat` object directly from this exported data. The model and messages will be loaded from the chat data, but tools are not saved and must be re-added.
```python
chat = Chat.from_json(chatdata)
```

You can also load the chat data into an existing `Chat` object. This will replace the model and messages with the provided data, but the list of tools will not change. This is often fasterand more useful if you are using the same set of tools but want to load a different chat history.
```python
chat.load_json(chatdata)
```
