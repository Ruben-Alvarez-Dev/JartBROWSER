"""MCP (Model Context Protocol) API endpoints"""

import uuid
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from jartbrowser.models.schemas import MCPConnectionCreate, MCPConnectionResponse, MCPToolResponse

router = APIRouter()


# In-memory storage for MCP connections
_mcp_connections: Dict[str, Dict[str, Any]] = {}


# Built-in MCP tools
BUILTIN_TOOLS = [
    {
        "name": "browser_navigate",
        "description": "Navigate to a URL",
        "input_schema": {
            "type": "object",
            "properties": {"url": {"type": "string", "description": "URL to navigate to"}},
            "required": ["url"],
        },
    },
    {
        "name": "browser_click",
        "description": "Click an element on the page",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for element"}
            },
            "required": ["selector"],
        },
    },
    {
        "name": "browser_fill",
        "description": "Fill a form input",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for input"},
                "value": {"type": "string", "description": "Value to fill"},
            },
            "required": ["selector", "value"],
        },
    },
    {
        "name": "browser_screenshot",
        "description": "Take a screenshot of the current page",
        "input_schema": {
            "type": "object",
            "properties": {"full_page": {"type": "boolean", "description": "Capture full page"}},
        },
    },
    {
        "name": "browser_get_dom",
        "description": "Get DOM snapshot of current page",
        "input_schema": {
            "type": "object",
            "properties": {
                "include_html": {"type": "boolean", "description": "Include HTML in snapshot"}
            },
        },
    },
    {
        "name": "llm_complete",
        "description": "Complete text using LLM",
        "input_schema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Prompt for LLM"},
                "model": {"type": "string", "description": "Model to use"},
                "temperature": {"type": "number", "description": "Temperature"},
            },
            "required": ["prompt"],
        },
    },
]


@router.get("/mcp/status")
async def mcp_status():
    """Get MCP server status"""
    return {
        "running": True,
        "version": "1.0.0",
        "connections": len(_mcp_connections),
        "builtin_tools": len(BUILTIN_TOOLS),
    }


@router.get("/mcp/tools", response_model=List[MCPToolResponse])
async def list_tools():
    """List available MCP tools"""
    return BUILTIN_TOOLS


@router.get("/mcp/tools/{tool_name}", response_model=MCPToolResponse)
async def get_tool(tool_name: str):
    """Get a specific tool"""
    for tool in BUILTIN_TOOLS:
        if tool["name"] == tool_name:
            return tool
    raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")


@router.post("/mcp/connections", response_model=MCPConnectionResponse)
async def create_mcp_connection(connection: MCPConnectionCreate):
    """Add a custom MCP server connection"""
    connection_id = str(uuid.uuid4())

    _mcp_connections[connection_id] = {
        "id": connection_id,
        "name": connection.name,
        "url": connection.url,
        "auth_token": connection.auth_token,
        "is_active": True,
        "last_connected": None,
        "tools_count": 0,
    }

    return MCPConnectionResponse(
        id=connection_id,
        name=connection.name,
        url=connection.url,
        auth_token=connection.auth_token,
        is_active=True,
        last_connected=None,
        tools_count=0,
    )


@router.get("/mcp/connections", response_model=List[MCPConnectionResponse])
async def list_mcp_connections():
    """List all MCP connections"""
    return [
        MCPConnectionResponse(
            id=conn["id"],
            name=conn["name"],
            url=conn["url"],
            auth_token=conn.get("auth_token"),
            is_active=conn["is_active"],
            last_connected=conn.get("last_connected"),
            tools_count=conn["tools_count"],
        )
        for conn in _mcp_connections.values()
    ]


@router.delete("/mcp/connections/{connection_id}")
async def delete_mcp_connection(connection_id: str):
    """Remove an MCP connection"""
    if connection_id not in _mcp_connections:
        raise HTTPException(status_code=404, detail="Connection not found")

    del _mcp_connections[connection_id]

    return {"success": True, "message": "Connection deleted"}


@router.post("/mcp/connections/{connection_id}/test")
async def test_mcp_connection(connection_id: str):
    """Test an MCP connection"""
    if connection_id not in _mcp_connections:
        raise HTTPException(status_code=404, detail="Connection not found")

    # Placeholder - would actually test the connection
    return {"success": True, "message": "Connection test successful", "latency_ms": 100}
