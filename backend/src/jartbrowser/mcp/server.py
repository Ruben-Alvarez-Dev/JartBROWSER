"""MCP (Model Context Protocol) Server"""

import asyncio
import json
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime
import sse_starlette.sse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


@dataclass
class MCPTool:
    """MCP Tool definition"""

    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Optional[Callable] = None


@dataclass
class MCPResource:
    """MCP Resource definition"""

    uri: str
    name: str
    description: str
    mime_type: str = "application/json"


@dataclass
class MCPrompt:
    """MCP Prompt definition"""

    name: str
    description: str
    arguments: List[Dict[str, Any]] = field(default_factory=list)


class MCPServer:
    """MCP Server implementation"""

    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.prompts: Dict[str, MCPrompt] = {}
        self._running = False
        self._app: Optional[FastAPI] = None

        # Register built-in tools
        self._register_builtin_tools()

    def _register_builtin_tools(self):
        """Register built-in MCP tools"""

        async def navigate_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            url = args.get("url")
            # Would communicate with Chrome extension
            return {"success": True, "url": url, "status": "navigated"}

        async def click_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            selector = args.get("selector")
            return {"success": True, "selector": selector, "action": "clicked"}

        async def fill_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            selector = args.get("selector")
            value = args.get("value")
            return {"success": True, "selector": selector, "value": value, "action": "filled"}

        async def screenshot_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            full_page = args.get("full_page", False)
            return {"success": True, "full_page": full_page, "image": "base64_data"}

        async def get_dom_handler(args: Dict[str, Any]) -> Dict[str, Any]:
            include_html = args.get("include_html", True)
            return {
                "success": True,
                "elements": [],
                "html": "<html>...</html>" if include_html else None,
                "text": "Page text",
            }

        # Register tools
        self.register_tool(
            MCPTool(
                name="browser_navigate",
                description="Navigate to a URL",
                input_schema={
                    "type": "object",
                    "properties": {"url": {"type": "string", "description": "URL to navigate to"}},
                    "required": ["url"],
                },
                handler=navigate_handler,
            )
        )

        self.register_tool(
            MCPTool(
                name="browser_click",
                description="Click an element on the page",
                input_schema={
                    "type": "object",
                    "properties": {"selector": {"type": "string", "description": "CSS selector"}},
                    "required": ["selector"],
                },
                handler=click_handler,
            )
        )

        self.register_tool(
            MCPTool(
                name="browser_fill",
                description="Fill a form input",
                input_schema={
                    "type": "object",
                    "properties": {
                        "selector": {"type": "string", "description": "CSS selector"},
                        "value": {"type": "string", "description": "Value to fill"},
                    },
                    "required": ["selector", "value"],
                },
                handler=fill_handler,
            )
        )

        self.register_tool(
            MCPTool(
                name="browser_screenshot",
                description="Take a screenshot",
                input_schema={
                    "type": "object",
                    "properties": {
                        "full_page": {"type": "boolean", "description": "Capture full page"}
                    },
                },
                handler=screenshot_handler,
            )
        )

        self.register_tool(
            MCPTool(
                name="browser_get_dom",
                description="Get DOM snapshot",
                input_schema={
                    "type": "object",
                    "properties": {
                        "include_html": {"type": "boolean", "description": "Include HTML"}
                    },
                },
                handler=get_dom_handler,
            )
        )

    def register_tool(self, tool: MCPTool):
        """Register a tool"""
        self.tools[tool.name] = tool

    def register_resource(self, resource: MCPResource):
        """Register a resource"""
        self.resources[resource.uri] = resource

    def register_prompt(self, prompt: MCPrompt):
        """Register a prompt"""
        self.prompts[prompt.name] = prompt

    def get_tools_list(self) -> List[Dict[str, Any]]:
        """Get list of tools"""
        return [
            {"name": tool.name, "description": tool.description, "inputSchema": tool.input_schema}
            for tool in self.tools.values()
        ]

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool"""
        if name not in self.tools:
            return {"error": f"Tool not found: {name}"}

        tool = self.tools[name]

        if tool.handler:
            try:
                return await tool.handler(arguments)
            except Exception as e:
                return {"error": str(e)}

        return {"error": "No handler registered"}

    async def start(self, host: str = "0.0.0.0", port: int = 3001):
        """Start MCP server"""
        self._running = True

        # Create FastAPI app for SSE endpoint
        self._app = FastAPI()

        @self._app.get("/sse")
        async def sse_endpoint(request: Request):
            """SSE endpoint for MCP"""

            async def event_generator():
                # Send initial capabilities
                yield {
                    "event": "message",
                    "data": json.dumps(
                        {
                            "jsonrpc": "2.0",
                            "method": "initialized",
                            "params": {
                                "protocolVersion": "2024-11-05",
                                "capabilities": {
                                    "tools": {"listChanged": True},
                                    "resources": {"listChanged": True},
                                    "prompts": {"listChanged": True},
                                },
                                "serverInfo": {
                                    "name": "JartBROWSER MCP Server",
                                    "version": "1.0.0",
                                },
                            },
                        }
                    ),
                }

                # Keep connection alive
                while self._running:
                    await asyncio.sleep(30)
                    yield {
                        "event": "message",
                        "data": json.dumps({"jsonrpc": "2.0", "method": "ping"}),
                    }

            return sse_starlette.EventSourceResponse(event_generator())

        @self._app.post("/messages")
        async def handle_message(request: Request):
            """Handle MCP JSON-RPC messages"""
            body = await request.json()

            method = body.get("method")
            params = body.get("params", {})
            msg_id = body.get("id")

            response = {"jsonrpc": "2.0", "id": msg_id}

            if method == "tools/list":
                response["result"] = {"tools": self.get_tools_list()}

            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self.call_tool(tool_name, arguments)
                response["result"] = {"content": [{"type": "text", "text": json.dumps(result)}]}

            elif method == "resources/list":
                response["result"] = {
                    "resources": [
                        {
                            "uri": r.uri,
                            "name": r.name,
                            "description": r.description,
                            "mimeType": r.mime_type,
                        }
                        for r in self.resources.values()
                    ]
                }

            elif method == "prompts/list":
                response["result"] = {
                    "prompts": [
                        {"name": p.name, "description": p.description, "arguments": p.arguments}
                        for p in self.prompts.values()
                    ]
                }

            else:
                response["error"] = {"code": -32601, "message": f"Method not found: {method}"}

            return JSONResponse(response)

        @self._app.get("/health")
        async def health():
            return {"status": "healthy", "mcp": True}

        # Note: In production, you'd use uvicorn to run this
        # For now, we just prepare the app
        print(f"MCP Server app created at http://{host}:{port}")

    async def stop(self):
        """Stop MCP server"""
        self._running = False


# Singleton instance
_mcp_server: Optional[MCPServer] = None


def get_mcp_server() -> MCPServer:
    """Get global MCP server instance"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = MCPServer()
    return _mcp_server
