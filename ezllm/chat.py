import requests
from ollama import Client
from .tools import Tool
import json
from .kickstart import kickstart
from time import sleep

default_model = "qwen3:latest"

class Chat:
    def __init__(self, model=default_model, url=None, hide_thoughts=True):
        self.url = url
        if url is None:
            self.container = kickstart()
            url = "http://localhost:11434"
        self.client = Client(host=url)
        self.model = model
        self.messages = []
        self.hide_thoughts = hide_thoughts
        self.tools = {}

    def add_tools(self, *tools):
        for tool in tools:
            if isinstance(tool, Tool):
                self.tools[tool.name] = tool
            elif hasattr(tool, "add_all_tools"):
                tool.add_all_tools(self)

    def _ensure_model(self):
        timeout = 0.1
        while timeout <= 2:
            try:
                for model in self.client.list().models:
                    if model.model == self.model:
                        return
                break
            except:
                sleep(timeout)
                timeout *= 2
                if timeout > 2:
                    raise
        print(f"Pulling model {self.model}...")
        self.client.pull(self.model)
        print(f"Successfully pulled {self.model}.")

    def to_json(self):
        return json.dumps({
                "url" : self.url,
                "model" : self.model,
                "messages" : self.messages,
                "hide_thoughts" : self.hide_thoughts,
                })

    def load_json(self, datastr):
        data = json.loads(datastr)
        self.model = data["model"]
        if self.url != data["url"]:
            self.url = data["url"]
            url = self.url
            if url is None:
                self.container = kickstart()
                url = "http://localhost:11434"
            self.client = Client(host=self.url)
        self.hide_thoughts = data["hide_thoughts"]
        self.messages = data["messages"]

    @classmethod
    def from_json(cls, datastr):
        data = json.loads(datastr)
        new_chat = cls(model=data["model"], url=data["url"], hide_thoughts=data["hide_thoughts"])
        new_chat.messages = data["messages"]
        return new_chat

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
            if "tool_calls" in message and message["tool_calls"] is not None:
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
        self._ensure_model()
        if text is not None:
            self.messages.append({
                "role" : "user",
                "content" : text,
                })
        payload_messages = self.messages
        tooldata = []
        if len(self.tools) > 0 and recursion_limit > 0:
            for toolname in self.tools:
                tool = self.tools[toolname]
                tooldata.append({"type" : "function", "function" : tool.dict()})
        data = self.client.chat(model=self.model, messages=self.messages, format=structure, tools=tooldata)
        if "context" in data:
            print(f"Got context: {self.context}")
        if "message" in data:
            response = data["message"]
            if "tool_calls" in response and response["tool_calls"] is not None and len(response["tool_calls"]) > 0:
                try:
                    response["tool_calls"] = [{'function' : {'name' : tool_call.function.name, "arguments" : tool_call.function.arguments}} for tool_call in response["tool_calls"]]
                except:
                    print(response['tool_calls'])
            mdict = {key: value for key, value in response if value is not None}
            self.messages.append(mdict)


            if "tool_calls" in response and response["tool_calls"] is not None and len(response["tool_calls"]) > 0:
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
                        "tool_name" : tool_call["name"],
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
