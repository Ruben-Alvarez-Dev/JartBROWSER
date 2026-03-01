"""API Schemas for JartBROWSER"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr


# ============== User Schemas ==============
class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=255)
    email: Optional[EmailStr] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ============== API Key Schemas ==============
class APIKeyBase(BaseModel):
    provider: str
    key_alias: Optional[str] = None


class APIKeyCreate(APIKeyBase):
    api_key: str


class APIKeyResponse(APIKeyBase):
    id: int
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime]

    class Config:
        from_attributes = True


# ============== Session Schemas ==============
class SessionBase(BaseModel):
    name: str


class SessionCreate(SessionBase):
    session_data: Optional[Dict[str, Any]] = None


class SessionUpdate(BaseModel):
    name: Optional[str] = None
    session_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SessionResponse(SessionBase):
    id: int
    user_id: int
    session_data: Optional[Dict[str, Any]]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Bookmark Schemas ==============
class BookmarkBase(BaseModel):
    url: str = Field(..., max_length=2048)
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[int] = None


class BookmarkCreate(BookmarkBase):
    pass


class BookmarkUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    folder_id: Optional[int] = None


class BookmarkResponse(BookmarkBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Prompt Template Schemas ==============
class PromptTemplateBase(BaseModel):
    name: str
    category: Optional[str] = None
    content: str
    variables: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class PromptTemplateCreate(PromptTemplateBase):
    pass


class PromptTemplateUpdate(BaseModel):
    content: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(PromptTemplateBase):
    id: int
    is_active: bool
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Skill Schemas ==============
class SkillBase(BaseModel):
    name: str
    category: Optional[str] = None
    description: Optional[str] = None
    definition: Dict[str, Any]


class SkillCreate(SkillBase):
    pass


class SkillUpdate(BaseModel):
    description: Optional[str] = None
    definition: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class SkillResponse(SkillBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Workflow Schemas ==============
class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    nodes: List[Dict[str, Any]]
    edges: Optional[List[Dict[str, Any]]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    nodes: Optional[List[Dict[str, Any]]] = None
    edges: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None


class WorkflowResponse(WorkflowBase):
    id: int
    user_id: int
    nodes: List[Dict[str, Any]]
    edges: Optional[List[Dict[str, Any]]]
    is_template: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============== Provider Schemas ==============
class ProviderConfig(BaseModel):
    provider: str
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=4096, ge=1)


class ProviderListResponse(BaseModel):
    providers: List[str]
    default_provider: str
    default_model: str


# ============== Docker Schemas ==============
class DockerStatusResponse(BaseModel):
    running: bool
    containers: List[Dict[str, Any]] = []
    images: List[Dict[str, Any]] = []
    volumes: List[Dict[str, Any]] = []


class DockerContainerAction(BaseModel):
    action: str  # start, stop, restart, remove
    container_id: str


class DockerComposeResponse(BaseModel):
    success: bool
    message: str
    containers: Optional[List[Dict[str, Any]]] = None


# ============== Health Schemas ==============
class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: float
    database: str
    mcp_server: bool


class InfoResponse(BaseModel):
    name: str
    version: str
    description: str
    api_version: str


# ============== MCP Schemas ==============
class MCPConnectionBase(BaseModel):
    name: str
    url: str
    auth_token: Optional[str] = None


class MCPConnectionCreate(MCPConnectionBase):
    pass


class MCPConnectionResponse(MCPConnectionBase):
    id: int
    is_active: bool
    last_connected: Optional[datetime]
    tools_count: int

    class Config:
        from_attributes = True


class MCPToolResponse(BaseModel):
    name: str
    description: Optional[str]
    input_schema: Dict[str, Any]


# ============== Browser Schemas ==============
class BrowserAction(BaseModel):
    action: str  # navigate, click, fill, submit, screenshot, etc.
    target: Optional[str] = None  # selector or URL
    value: Optional[str] = None
    options: Optional[Dict[str, Any]] = None


class BrowserActionResponse(BaseModel):
    success: bool
    action: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class TabInfo(BaseModel):
    id: int
    url: str
    title: str
    active: bool
    pinned: bool


class WindowInfo(BaseModel):
    id: int
    focused: bool
    tabs: List[TabInfo]


# ============== Agent Schemas ==============
class AgentTask(BaseModel):
    task: str
    context: Optional[Dict[str, Any]] = None
    max_steps: int = Field(default=10, ge=1, le=100)


class AgentTaskResponse(BaseModel):
    task_id: str
    status: str  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    steps_completed: int = 0


class AgentStatusResponse(BaseModel):
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_tokens_used: int = 0
