# Services package initialization

from jartbrowser.services.database import DatabaseService, get_database_service
from jartbrowser.services.encryption import EncryptionService, get_encryption_service
from jartbrowser.services.llm_provider import (
    BaseLLMProvider,
    OpenAIProvider,
    AnthropicProvider,
    OllamaProvider,
    get_provider,
    PROVIDER_MODELS,
)
from jartbrowser.services.llm_service import (
    LLMService,
    ModelInfo,
    LLMResponse,
    Conversation,
    get_llm_service,
    MODEL_REGISTRY,
)
from jartbrowser.services.browser_automation import (
    BrowserAutomationService,
    BrowserAction,
    Tab,
    Window,
    ActionType,
    get_browser_service,
)
from jartbrowser.services.bookmark import (
    BookmarkService,
    Bookmark,
    BookmarkFolder,
    get_bookmark_service,
)
from jartbrowser.services.history import HistoryService, HistoryEntry, get_history_service
from jartbrowser.services.privacy import (
    PrivacyService,
    PrivacySettings,
    SecuritySettings,
    PrivacyMode,
    DataLocation,
    get_privacy_service,
)
from jartbrowser.services.multi_tab import (
    MultiTabCoordinationService,
    CrossTabMessage,
    CoordinationEvent,
    get_coordination_service,
)
from jartbrowser.services.tab_search import (
    TabSearchService,
    TabIndex,
    SearchResult,
    get_tab_search_service,
)
from jartbrowser.services.dom_scanner import (
    DOMScannerService,
    PageStructure,
    ElementInfo,
    ElementType,
    get_dom_scanner_service,
)
from jartbrowser.services.session_persistence import (
    SessionPersistenceService,
    SessionData,
    get_session_service,
)
from jartbrowser.services.audit_log import (
    AuditLogService,
    AuditLogEntry,
    AuditAction,
    AuditLevel,
    get_audit_service,
)
from jartbrowser.services.audit_log import (
    AuditLogService,
    AuditLogEntry,
    AuditAction,
    AuditLevel,
    get_audit_service,
)
from jartbrowser.services.workflow import (
    WorkflowBuilderService,
    Workflow,
    WorkflowNode,
    WorkflowEdge,
    WorkflowExecution,
    NodeType,
    TriggerType,
    EdgeType,
    get_workflow_service,
)
from jartbrowser.services.task_scheduler import (
    TaskSchedulerService,
    ScheduledTask,
    TaskExecution,
    ScheduleType,
    TaskStatus,
    TaskPriority,
    get_task_scheduler,
)
from jartbrowser.services.agent_persistence import (
    AgentPersistenceService,
    AgentSession,
    AgentCheckpoint,
    RecoveryResult,
    AgentState,
    RecoveryPoint,
    RecoveryStatus,
    get_agent_persistence,
)
from jartbrowser.services.vision import (
    VisionService,
    VisionCapture,
    OCRResult,
    VisualElement,
    ScreenRegion,
    VisionCaptureType,
    OCREngine,
    get_vision_service,
)
from jartbrowser.services.mcp_integration import (
    MCPIntegrationService,
    MCPTool,
    MCPResource,
    MCPPrompt,
    MCPClient,
    MCPProtocolVersion,
    MCPResourceType,
    MCPToolVisibility,
    get_mcp_service,
)
from jartbrowser.services.error_recovery import (
    ErrorRecoveryService,
    ErrorRecord,
    CircuitBreaker,
    RecoveryAction,
    SelfHealingRule,
    ErrorSeverity,
    ErrorCategory,
    RecoveryStrategy,
    CircuitState,
    get_error_recovery_service,
)
from jartbrowser.services.window_persistence import (
    WindowPersistenceService,
    WindowProfile,
    WindowGeometry,
    WindowGroup,
    WindowState,
    WindowType,
    MonitorInfo,
    get_window_persistence,
)

__all__ = [
    # Database
    "DatabaseService",
    "get_database_service",
    # Encryption
    "EncryptionService",
    "get_encryption_service",
    # LLM Providers
    "BaseLLMProvider",
    "OpenAIProvider",
    "AnthropicProvider",
    "OllamaProvider",
    "get_provider",
    "PROVIDER_MODELS",
    # LLM Service
    "LLMService",
    "ModelInfo",
    "LLMResponse",
    "Conversation",
    "get_llm_service",
    "MODEL_REGISTRY",
    # Browser Automation
    "BrowserAutomationService",
    "BrowserAction",
    "Tab",
    "Window",
    "ActionType",
    "get_browser_service",
    # Bookmark
    "BookmarkService",
    "Bookmark",
    "BookmarkFolder",
    "get_bookmark_service",
    # History
    "HistoryService",
    "HistoryEntry",
    "get_history_service",
    # Privacy
    "PrivacyService",
    "PrivacySettings",
    "SecuritySettings",
    "PrivacyMode",
    "DataLocation",
    "get_privacy_service",
    # Multi-Tab Coordination
    "MultiTabCoordinationService",
    "CrossTabMessage",
    "CoordinationEvent",
    "get_coordination_service",
    # Tab Search
    "TabSearchService",
    "TabIndex",
    "SearchResult",
    "get_tab_search_service",
    # DOM Scanner
    "DOMScannerService",
    "PageStructure",
    "ElementInfo",
    "ElementType",
    "get_dom_scanner_service",
    # Session Persistence
    "SessionPersistenceService",
    "SessionData",
    "get_session_service",
    # Audit Log
    "AuditLogService",
    "AuditLogEntry",
    "AuditAction",
    "AuditLevel",
    "get_audit_service",
    # Workflow
    "WorkflowBuilderService",
    "Workflow",
    "WorkflowNode",
    "WorkflowEdge",
    "WorkflowExecution",
    "NodeType",
    "TriggerType",
    "EdgeType",
    "get_workflow_service",
    # Task Scheduler
    "TaskSchedulerService",
    "ScheduledTask",
    "TaskExecution",
    "ScheduleType",
    "TaskStatus",
    "TaskPriority",
    "get_task_scheduler",
    # Agent Persistence
    "AgentPersistenceService",
    "AgentSession",
    "AgentCheckpoint",
    "RecoveryResult",
    "AgentState",
    "RecoveryPoint",
    "RecoveryStatus",
    "get_agent_persistence",
    # Vision
    "VisionService",
    "VisionCapture",
    "OCRResult",
    "VisualElement",
    "ScreenRegion",
    "VisionCaptureType",
    "OCREngine",
    "get_vision_service",
    # MCP Integration
    "MCPIntegrationService",
    "MCPTool",
    "MCPResource",
    "MCPPrompt",
    "MCPClient",
    "MCPProtocolVersion",
    "MCPResourceType",
    "MCPToolVisibility",
    "get_mcp_service",
    # Error Recovery
    "ErrorRecoveryService",
    "ErrorRecord",
    "CircuitBreaker",
    "RecoveryAction",
    "SelfHealingRule",
    "ErrorSeverity",
    "ErrorCategory",
    "RecoveryStrategy",
    "CircuitState",
    "get_error_recovery_service",
    # Window Persistence
    "WindowPersistenceService",
    "WindowProfile",
    "WindowGeometry",
    "WindowGroup",
    "WindowState",
    "WindowType",
    "MonitorInfo",
    "get_window_persistence",
]
