import requests
from .tools import Tool

models = [
        "qwen2.5:32b",
        "codellama:34b",
        "qwen2.5-coder:32b",
        "qwen3:32b",
        "llama3.2:latest",
        "deepseek-r1:32b",
        ]
default_model = "qwen3:32b"

class Conversation:
    def __init__(self, model=default_model, url="http://localhost:11434", hide_thoughts=True):
        self.model = model
        self.context = None
        self.hide_thoughts = hide_thoughts
        self.url = url

    def memory_wipe(self):
        self.context = None

    def prompt(self, text):
        payload = {
                "model" : self.model,
                "prompt" : text,
                "stream" : False,
                }
        if self.context is not None:
            payload["context"] = self.context

        data = requests.post(self.url + "/api/generate", json=payload).json()
        response = data["response"]
        if self.hide_thoughts and "deepseek" in self.model:
            parts = response.split("</think>")
            if len(parts) > 1:
                response = parts[1]
            else:
                response = parts[0]
        self.context = data["context"]
        return response


class Chat:
    def __init__(self, model=default_model, url="http://localhost:11434", hide_thoughts=True):
        self.model = model
        self.messages = []
        self.hide_thoughts = hide_thoughts
        self.url = url
        self.tools = {}
        self.system("If the user asks a question for something that can be verified using your tools, such as a math or science related question, remember to use those tools to inform your answer.")

    def add_tool(self, tool):
        assert isinstance(tool, Tool)
        self.tools[tool.name] = tool

    def memory_wipe(self):
        self.messages = []
    
    def system(self, message):
        self.system_prompt = message

    def print(self):
        max_name_len = 0
        for message in self.messages:
            name = message['role']
            if len(name) > max_name_len:
                max_name_len = len(name)
        max_name_len += 1
        for message in self.messages:
            if "tool_calls" in message:
                msg = None
                for tool_call in message["tool_calls"]:
                    if msg is None:
                        msg = ""
                    else:
                        msg += "\n"
                    msg += f"{tool_call['function']['name']}("
                    for arg in tool_call['function']['arguments']:
                        msg += f"{arg}={repr(tool_call['function']['arguments'][arg])}, "
                    msg += ")"
            else:
                msg = message['content']
            print(f"{message['role']}:{' ' * (max_name_len - len(message['role']))}{msg}\n")

    def query(self, message, query):
        def str_for_type(t):
            if t is int:
                return "integer"
            elif t is bool:
                return "boolean"
            elif t is float:
                return "number"
            else:
                return "string"
        if isinstance(query, dict):
            properties = dict()
            for key in query:
                if key in ["required", "optional"]:
                    continue
                properties[key] = {"type" : str_for_type(query[key])}
            if "required" in query:
                required = query["required"]
            elif "optional" in query:
                required = [k for k in query if k not in query["optional"]]
            else:
                required = [k for k in query]
        else:
            properties = dict()
            required = []
            for entry in query:
                required.append(entry)
                properties[entry] = {"type" : "string"}

        structure = {
                    "type" : "object",
                    "properties" : properties,
                    "required" : required,
                    }
        return self.prompt(message, structure=structure)

    def prompt(self, text, recursion_limit=10, structure=None, suffix=None):
        if text is not None:
            self.messages.append({
                "role" : "user",
                "content" : text,
                })
        #payload_messages = self.messages[:-1] + [{"role" : "system",  "content" : self.system}] + [self.messages[-1]]
        payload_messages = [{"role" : "system", "content" : self.system_prompt}] + self.messages
        payload = {
                "model" : self.model,
                "messages" : payload_messages,
                "stream" : False,
                }
        if structure is not None:
            payload["format"] = structure
        if len(self.tools) > 0 and recursion_limit > 0:
            tooldata = []
            for toolname in self.tools:
                tool = self.tools[toolname]
                tooldata.append({"type" : "function", "function" : tool.dict()})
            payload["tools"] = tooldata

        data = requests.post(self.url + "/api/chat", json=payload).json()
        if "message" in data:
            response = data["message"]
            self.messages.append(response)

            if "tool_calls" in response and len(response["tool_calls"]) > 0:
                for tool_call in response["tool_calls"]:
                    if not "function" in tool_call:
                        print(f"UNKNOWN TOOL CALL: {tool_call}")
                    tool_call = tool_call["function"]
                    if tool_call["name"] not in self.tools:
                        print(f"UNKNOWN TOOL: {tool_call}")
                    kwargs = tool_call["arguments"]
                    result = self.tools[tool_call["name"]](**kwargs)
                    self.messages.append({
                        "role" : "tool",
                        "content" : f"{result}",
                        "name" : tool_call["name"],
                        })
                if recursion_limit > 0:
                    return self.prompt(None, recursion_limit-1)


            text = response["content"]
            if self.hide_thoughts and "<think>" in text:
                parts = text.split("</think>")
                if len(parts) > 1:
                    text = parts[1]
                else:
                    text = parts[0]

            return text
        else:
            for message in self.messages:
                print(message)
            print(data)
            return data

