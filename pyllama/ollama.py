import requests
from .tools import Tool

default_model = "qwen3:latest"

class Chat:
    def __init__(self, model=default_model, url="http://localhost:11434", hide_thoughts=True):
        self.model = model
        self.messages = []
        self.hide_thoughts = hide_thoughts
        self.url = url
        self.tools = {}

    def add_tool(self, tool):
        assert isinstance(tool, Tool)
        self.tools[tool.name] = tool

    def memory_wipe(self):
        self.messages = []
    
    def system(self, message):
        self.system_prompt = message

    def get_log(self):
        max_name_len = 0
        for message in self.messages:
            name = message['role']
            if len(name) > max_name_len:
                max_name_len = len(name)
        max_name_len += 1
        logstr = ""
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
            logstr += f"{message['role']}:{' ' * (max_name_len - len(message['role']))}{msg}\n\n"
        return logstr

    def print(self):
        print(self.get_log())

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
        payload_messages = self.messages
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

