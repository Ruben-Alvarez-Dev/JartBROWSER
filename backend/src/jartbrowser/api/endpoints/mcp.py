from fastapi import APIRouter
from jartbrowser.services.mcp_integration import (
    MCPIntegrationService,
    MCPResourceType,
    MCPToolVisibility,
    get_mcp_service,
)
from pydantic import BaseModel
from typing import Optional, Dict, Any

router = APIRouter()


@router.get("/mcp/tools")
async def list_tools():
    return {"tools": []}


class ToolCreate(BaseModel):
    name: str


@router.post("/mcp/tools")
async def register_tool(payload: ToolCreate):
    return {"registered_tool": payload.name}


@router.delete("/mcp/tools/{tool_id}")
async def unregister_tool(tool_id: str):
    return {"unregistered_tool": tool_id}


class ToolExecute(BaseModel):
    args: Optional[Dict[str, Any]] = None


@router.post("/mcp/tools/{name}/execute")
async def execute_tool(name: str, payload: ToolExecute):
    return {"executed_tool": name, "args": payload.args or {}}


@router.get("/mcp/resources")
async def list_resources():
    return {"resources": []}


class ResourceCreate(BaseModel):
    name: str


@router.post("/mcp/resources")
async def register_resource(payload: ResourceCreate):
    return {"registered_resource": payload.name}


@router.get("/mcp/resources/{id}")
async def read_resource(id: str):
    return {"resource": {"id": id}}


@router.get("/mcp/prompts")
async def list_prompts():
    return {"prompts": []}


class PromptCreate(BaseModel):
    name: str


@router.post("/mcp/prompts")
async def register_prompt(payload: PromptCreate):
    return {"registered_prompt": payload.name}


class RenderPrompt(BaseModel):
    context: Optional[Dict[str, Any]] = None


@router.post("/mcp/prompts/{name}/render")
async def render_prompt(name: str, payload: RenderPrompt):
    return {"rendered_prompt": name, "context": payload.context}


@router.get("/mcp/clients")
async def list_clients():
    return {"clients": []}


class ClientConnect(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None


@router.post("/mcp/clients")
async def connect_client(payload: ClientConnect):
    return {"connected_client": payload.name or payload.id}


@router.delete("/mcp/clients/{id}")
async def disconnect_client(id: str):
    return {"disconnected": id}
