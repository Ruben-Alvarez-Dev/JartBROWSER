"""
MCP Integration Service

Provides MCP (Model Context Protocol) server and client functionality.
"""

import uuid
import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
from abc import ABC, abstractmethod
import aiohttp


class MCPProtocolVersion(Enum):
    """MCP protocol versions"""

    V1 = "2024-11-05"
    V2 = "2024-12-06"


class MCPResourceType(Enum):
    """MCP resource types"""

    FILE = "file"
    URL = "url"
    DATABASE = "database"
    API = "api"
    CUSTOM = "custom"


class MCPToolVisibility(Enum):
    """MCP tool visibility"""

    PRIVATE = "private"
    PROTECTED = "protected"
    PUBLIC = "public"


@dataclass
class MCPTool:
    """MCP tool definition"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    input_schema: Dict[str, Any] = field(default_factory=dict)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    visibility: MCPToolVisibility = MCPToolVisibility.PROTECTED
    handler: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema,
            "outputSchema": self.output_schema,
            "visibility": self.visibility.value,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
        }


@dataclass
class MCPResource:
    """MCP resource"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    uri: str = ""
    resource_type: MCPResourceType = MCPResourceType.FILE
    mime_type: Optional[str] = None
    description: str = ""
    size: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "uri": self.uri,
            "type": self.resource_type.value,
            "mimeType": self.mime_type,
            "description": self.description,
            "size": self.size,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
        }


@dataclass
class MCPPrompt:
    """MCP prompt template"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    arguments: List[Dict[str, Any]] = field(default_factory=list)
    template: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "arguments": self.arguments,
            "template": self.template,
            "metadata": self.metadata,
            "createdAt": self.created_at.isoformat(),
        }


@dataclass
class MCPRequest:
    """MCP request"""

    jsonrpc: str = "2.0"
    id: Optional[str] = None
    method: str = ""
    params: Optional[Dict[str, Any]] = None


@dataclass
class MCPResponse:
    """MCP response"""

    jsonrpc: str = "2.0"
    id: Optional[str] = None
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


class MCPClient(ABC):
    """MCP client interface"""

    @abstractmethod
    async def connect(self) -> bool:
        """Connect to MCP server"""
        pass

    @abstractmethod
    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        pass

    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool"""
        pass

    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        pass

    @abstractmethod
    async def read_resource(self, uri: str) -> Any:
        """Read a resource"""
        pass

    @abstractmethod
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        pass


class MCPClientImpl(MCPClient):
    """MCP client implementation"""

    def __init__(self, server_url: str, api_key: Optional[str] = None):
        self.server_url = server_url
        self.api_key = api_key
        self._session: Optional[aiohttp.ClientSession] = None
        self._connected = False
        self._protocol_version = MCPProtocolVersion.V1
        self._tools: List[Dict[str, Any]] = []
        self._resources: List[Dict[str, Any]] = []

    async def connect(self) -> bool:
        """Connect to MCP server"""
        try:
            self._session = aiohttp.ClientSession()

            # Initialize connection
            request = MCPRequest(
                id=str(uuid.uuid4()),
                method="initialize",
                params={
                    "protocolVersion": self._protocol_version.value,
                    "capabilities": {},
                    "clientInfo": {
                        "name": "jartbrowser",
                        "version": "1.0.0",
                    },
                },
            )

            response = await self._send_request(request)
            if response and not response.error:
                self._connected = True
                # Fetch tools and resources
                await self._refresh_capabilities()
                return True

            return False
        except Exception:
            return False

    async def disconnect(self) -> None:
        """Disconnect from MCP server"""
        if self._session:
            await self._session.close()
            self._session = None
        self._connected = False

    async def _send_request(self, request: MCPRequest) -> Optional[MCPResponse]:
        """Send request to MCP server"""
        if not self._session:
            return None

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            async with self._session.post(
                self.server_url,
                json={
                    "jsonrpc": request.jsonrpc,
                    "id": request.id,
                    "method": request.method,
                    "params": request.params,
                },
                headers=headers,
            ) as resp:
                data = await resp.json()
                return MCPResponse(
                    jsonrpc=data.get("jsonrpc", "2.0"),
                    id=data.get("id"),
                    result=data.get("result"),
                    error=data.get("error"),
                )
        except Exception:
            return None

    async def _refresh_capabilities(self) -> None:
        """Refresh tools and resources"""
        self._tools = await self.list_tools()
        self._resources = await self.list_resources()

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool"""
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="tools/call",
            params={"name": tool_name, "arguments": arguments},
        )

        response = await self._send_request(request)
        return response.result if response else None

    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools"""
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="tools/list",
        )

        response = await self._send_request(request)
        if response and response.result:
            return response.result.get("tools", [])
        return []

    async def read_resource(self, uri: str) -> Any:
        """Read a resource"""
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="resources/read",
            params={"uri": uri},
        )

        response = await self._send_request(request)
        return response.result if response else None

    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources"""
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method="resources/list",
        )

        response = await self._send_request(request)
        if response and response.result:
            return response.result.get("resources", [])
        return []


class MCPIntegrationService:
    """
    Service for MCP integration.

    Provides:
    - MCP server functionality
    - MCP client connections
    - Tool registration and management
    - Resource management
    - Prompt templates
    """

    def __init__(self):
        self._tools: Dict[str, MCPTool] = {}
        self._resources: Dict[str, MCPResource] = {}
        self._prompts: Dict[str, MCPPrompt] = {}
        self._clients: Dict[str, MCPClient] = {}
        self._tool_handlers: Dict[str, Callable[..., Awaitable[Any]]] = {}
        self._protocol_version = MCPProtocolVersion.V1
        self._server_port = 8765

    # ============== Server Tools ==============

    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable[..., Awaitable[Any]],
        visibility: MCPToolVisibility = MCPToolVisibility.PROTECTED,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MCPTool:
        """Register a tool"""
        tool = MCPTool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            visibility=visibility,
            metadata=metadata or {},
        )

        self._tools[tool.id] = tool
        self._tool_handlers[name] = handler

        return tool

    def get_tool(self, tool_id: str = None, name: str = None) -> Optional[MCPTool]:
        """Get a tool"""
        if tool_id:
            return self._tools.get(tool_id)
        if name:
            return next((t for t in self._tools.values() if t.name == name), None)
        return None

    def get_tools(
        self,
        visibility: Optional[MCPToolVisibility] = None,
        limit: int = 50,
    ) -> List[MCPTool]:
        """Get tools"""
        results = list(self._tools.values())

        if visibility:
            results = [t for t in results if t.visibility == visibility]

        return results[:limit]

    def unregister_tool(self, tool_id: str) -> bool:
        """Unregister a tool"""
        if tool_id in self._tools:
            tool = self._tools[tool_id]
            if tool.name in self._tool_handlers:
                del self._tool_handlers[tool.name]
            del self._tools[tool_id]
            return True
        return False

    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """Execute a tool"""
        handler = self._tool_handlers.get(tool_name)
        if not handler:
            return {"error": f"Tool not found: {tool_name}"}

        try:
            result = await handler(arguments)
            return result
        except Exception as e:
            return {"error": str(e)}

    # ============== Resources ==============

    def register_resource(
        self,
        name: str,
        uri: str,
        resource_type: MCPResourceType,
        mime_type: Optional[str] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MCPResource:
        """Register a resource"""
        resource = MCPResource(
            name=name,
            uri=uri,
            resource_type=resource_type,
            mime_type=mime_type,
            description=description,
            metadata=metadata or {},
        )

        self._resources[resource.id] = resource
        return resource

    def get_resource(self, resource_id: str = None, uri: str = None) -> Optional[MCPResource]:
        """Get a resource"""
        if resource_id:
            return self._resources.get(resource_id)
        if uri:
            return next((r for r in self._resources.values() if r.uri == uri), None)
        return None

    def get_resources(
        self,
        resource_type: Optional[MCPResourceType] = None,
        limit: int = 50,
    ) -> List[MCPResource]:
        """Get resources"""
        results = list(self._resources.values())

        if resource_type:
            results = [r for r in results if r.resource_type == resource_type]

        return results[:limit]

    def unregister_resource(self, resource_id: str) -> bool:
        """Unregister a resource"""
        if resource_id in self._resources:
            del self._resources[resource_id]
            return True
        return False

    async def read_resource(self, resource_id: str) -> Optional[Any]:
        """Read a resource"""
        resource = self._resources.get(resource_id)
        if not resource:
            return None

        # In production, would read actual resource
        return {"uri": resource.uri, "data": None}

    # ============== Prompts ==============

    def register_prompt(
        self,
        name: str,
        description: str,
        template: str,
        arguments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MCPPrompt:
        """Register a prompt"""
        prompt = MCPPrompt(
            name=name,
            description=description,
            template=template,
            arguments=arguments or [],
            metadata=metadata or {},
        )

        self._prompts[prompt.id] = prompt
        return prompt

    def get_prompt(self, prompt_id: str = None, name: str = None) -> Optional[MCPPrompt]:
        """Get a prompt"""
        if prompt_id:
            return self._prompts.get(prompt_id)
        if name:
            return next((p for p in self._prompts.values() if p.name == name), None)
        return None

    def get_prompts(self, limit: int = 50) -> List[MCPPrompt]:
        """Get prompts"""
        results = list(self._prompts.values())
        return results[:limit]

    def render_prompt(
        self,
        prompt_name: str,
        arguments: Dict[str, Any],
    ) -> Optional[str]:
        """Render a prompt with arguments"""
        prompt = self.get_prompt(name=prompt_name)
        if not prompt:
            return None

        template = prompt.template
        for key, value in arguments.items():
            template = template.replace(f"{{{key}}}", str(value))

        return template

    def unregister_prompt(self, prompt_id: str) -> bool:
        """Unregister a prompt"""
        if prompt_id in self._prompts:
            del self._prompts[prompt_id]
            return True
        return False

    # ============== MCP Clients ==============

    async def connect_client(
        self,
        client_id: str,
        server_url: str,
        api_key: Optional[str] = None,
    ) -> bool:
        """Connect to an MCP server"""
        client = MCPClientImpl(server_url, api_key)
        success = await client.connect()

        if success:
            self._clients[client_id] = client

        return success

    async def disconnect_client(self, client_id: str) -> bool:
        """Disconnect from an MCP server"""
        client = self._clients.get(client_id)
        if not client:
            return False

        await client.disconnect()
        del self._clients[client_id]
        return True

    def get_client(self, client_id: str) -> Optional[MCPClient]:
        """Get an MCP client"""
        return self._clients.get(client_id)

    async def call_client_tool(
        self,
        client_id: str,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Any:
        """Call a tool on an MCP client"""
        client = self._clients.get(client_id)
        if not client:
            return {"error": f"Client not found: {client_id}"}

        return await client.call_tool(tool_name, arguments)

    async def list_client_tools(self, client_id: str) -> List[Dict[str, Any]]:
        """List tools on an MCP client"""
        client = self._clients.get(client_id)
        if not client:
            return []

        return await client.list_tools()

    async def read_client_resource(self, client_id: str, uri: str) -> Any:
        """Read a resource from an MCP client"""
        client = self._clients.get(client_id)
        if not client:
            return {"error": f"Client not found: {client_id}"}

        return await client.read_resource(uri)

    # ============== Server ==============

    async def start_server(self, port: int = 8765) -> None:
        """Start MCP server"""
        self._server_port = port
        # In production, would start actual MCP server
        pass

    async def stop_server(self) -> None:
        """Stop MCP server"""
        # In production, would stop MCP server
        pass

    def get_server_info(self) -> Dict[str, Any]:
        """Get server information"""
        return {
            "name": "JartBROWSER MCP Server",
            "version": "1.0.0",
            "protocolVersion": self._protocol_version.value,
            "toolsCount": len(self._tools),
            "resourcesCount": len(self._resources),
            "promptsCount": len(self._prompts),
            "clientsCount": len(self._clients),
            "port": self._server_port,
        }


# Singleton
_mcp_service: Optional[MCPIntegrationService] = None


def get_mcp_service() -> MCPIntegrationService:
    """Get the MCP integration service instance"""
    global _mcp_service
    if _mcp_service is None:
        _mcp_service = MCPIntegrationService()
    return _mcp_service
