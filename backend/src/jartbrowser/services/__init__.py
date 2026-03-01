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
]
