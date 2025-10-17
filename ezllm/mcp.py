from fastmcp import Client
import asyncio
from .tools import Tool


class MCPTool(Tool):
    def __init__(self, client, tooldata):
        self.client = client
        self.tooldata = tooldata
        self.name = tooldata["name"]
        self.kind = tooldata["kind"]

    def dict(self):
        return self.tooldata

    def __call__(self, *args, **kwargs):
        return self.client.await_tool(self, kwargs)

class MCPClient():
    def __init__(self, config):
        self.client = Client(config)
        self.tool_data = []
        asyncio.run(self.populate_tool_data())

    async def populate_tool_data(self):
        async with self.client:
            try:
                tool_list = await self.client.list_tools()
            except:
                tool_list = []
            for tool in tool_list:
                self.tool_data.append({
                    "name" : tool.name,
                    "description" : tool.description,
                    "parameters" : tool.inputSchema,
                    "kind" : "tool",
                    })

            try:
                resource_list = await self.client.list_resources()
            except:
                resource_list = []
            for resource in resource_list:
                self.tool_data.append({
                    "name" : resource.name,
                    "description" : resource.description,
                    "parameters" : {"properties" : {}, "required" : []},
                    "uri" : resource.uri,
                    "kind" : "resource",
                    })

    async def call_tool(self, tool, kwargs):
        async with self.client:
            if tool.kind == "tool":
                result = await self.client.call_tool(tool.name, kwargs)
                if result.structured_content is not None:
                    return result.structured_content
                else:
                    return result.content
            elif tool.kind == "resource":
                result = await self.client.read_resource(tool.tooldata["uri"])
                return result

    def await_tool(self, tool, kwargs):
        return asyncio.run(self.call_tool(tool, kwargs))


    def get_tools(self):
        return [MCPTool(self, data) for data in self.tool_data]

    def add_all_tools(self, chat):
        chat.add_tools(*self.get_tools())
