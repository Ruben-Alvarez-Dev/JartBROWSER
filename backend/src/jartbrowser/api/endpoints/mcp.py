from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from jartbrowser.services.mcp_integration import (
    MCPIntegrationService,
    MCPResourceType,
    MCPToolVisibility,
    get_mcp_service,
)


router = APIRouter()

# Obtain the singleton MCP service
service: MCPIntegrationService = get_mcp_service()


# Helper to invoke MCP service methods safely (dynamic dispatch)
def _call_method(method_name: str, *args, **kwargs):
    fn = getattr(service, method_name, None)
    if callable(fn):
        return fn(*args, **kwargs)
    raise HTTPException(status_code=501, detail=f"MCP service does not implement {method_name}")


class ToolCreate(BaseModel):
    name: str
    config: Optional[Dict[str, Any]] = None
    visibility: Optional[MCPToolVisibility] = None


class ToolExecute(BaseModel):
    args: Optional[Dict[str, Any]] = None


class ResourceCreate(BaseModel):
    name: str
    type: Optional[MCPResourceType] = None
    metadata: Optional[Dict[str, Any]] = None


class ResourceRead(BaseModel):
    # opaque read-only descriptor; kept for type hints
    id: str


class PromptCreate(BaseModel):
    name: str
    template: Optional[str] = None
    params: Optional[Dict[str, Any]] = None


class RenderPrompt(BaseModel):
    context: Optional[Dict[str, Any]] = None


class ClientConnect(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


@router.get("/mcp/tools")
async def list_tools():
    try:
        return _call_method("list_tools")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/tools")
async def register_tool(payload: ToolCreate):
    try:
        return _call_method("register_tool", payload.dict(exclude_none=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/mcp/tools/{tool_id}")
async def unregister_tool(tool_id: str):
    try:
        return _call_method("unregister_tool", tool_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/tools/{name}/execute")
async def execute_tool(name: str, payload: ToolExecute):
    try:
        return _call_method("execute_tool", name, payload.args or {})
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/resources")
async def list_resources():
    try:
        return _call_method("list_resources")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/resources")
async def register_resource(payload: ResourceCreate):
    try:
        return _call_method("register_resource", payload.dict(exclude_none=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/resources/{id}")
async def read_resource(id: str):
    try:
        return _call_method("read_resource", id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/prompts")
async def list_prompts():
    try:
        return _call_method("list_prompts")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/prompts")
async def register_prompt(payload: PromptCreate):
    try:
        return _call_method("register_prompt", payload.dict(exclude_none=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/prompts/{name}/render")
async def render_prompt(name: str, payload: RenderPrompt):
    try:
        return _call_method("render_prompt", name, payload.dict(exclude_none=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/mcp/clients")
async def list_clients():
    try:
        return _call_method("list_clients")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/mcp/clients")
async def connect_client(payload: ClientConnect):
    try:
        return _call_method("connect_client", payload.dict(exclude_none=True))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/mcp/clients/{id}")
async def disconnect_client(id: str):
    try:
        return _call_method("disconnect_client", id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
