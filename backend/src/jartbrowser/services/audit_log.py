"""
Audit Logging Service

Provides comprehensive audit logging for compliance,
tracking all agent actions, API calls, and user activities.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import json


class AuditAction(Enum):
    """Audit action types"""

    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"

    # API
    API_CALL = "api_call"
    API_KEY_CREATED = "api_key_created"
    API_KEY_DELETED = "api_key_deleted"

    # Browser
    TAB_CREATED = "tab_created"
    TAB_CLOSED = "tab_closed"
    TAB_NAVIGATED = "tab_navigated"
    ACTION_EXECUTED = "action_executed"
    SCREENSHOT_TAKEN = "screenshot_taken"

    # LLM
    LLM_REQUEST = "llm_request"
    MODEL_CHANGED = "model_changed"

    # Data
    BOOKMARK_CREATED = "bookmark_created"
    BOOKMARK_DELETED = "bookmark_deleted"
    SESSION_SAVED = "session_saved"
    SESSION_RESTORED = "session_restored"
    DATA_EXPORTED = "data_exported"
    DATA_IMPORTED = "data_imported"

    # Settings
    SETTINGS_CHANGED = "settings_changed"
    PRIVACY_CHANGED = "privacy_changed"

    # Admin
    USER_CREATED = "user_created"
    USER_DELETED = "user_deleted"
    ROLE_CHANGED = "role_changed"


class AuditLevel(Enum):
    """Audit log levels"""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditLogEntry:
    """Audit log entry"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    action: AuditAction = AuditAction.API_CALL
    level: AuditLevel = AuditLevel.INFO
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "user_id": self.user_id,
            "action": self.action.value,
            "level": self.level.value,
            "resource_type": self.resource_type,
            "resource_id": self.resource_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "session_id": self.session_id,
            "request_id": self.request_id,
            "success": self.success,
            "error_message": self.error_message,
        }


class AuditLogService:
    """
    Service for audit logging.

    Provides:
    - Comprehensive action logging
    - Search and filtering
    - Export functionality
    - Retention policies
    """

    def __init__(self):
        self._logs: Dict[str, AuditLogEntry] = {}
        self._user_index: Dict[str, Set[str]] = {}  # user_id -> log IDs
        self._action_index: Dict[AuditAction, Set[str]] = {}  # action -> log IDs
        self._retention_days: int = 90
        self._enabled: bool = True

    # ============== Logging ==============

    def log(
        self,
        action: AuditAction,
        level: AuditLevel = AuditLevel.INFO,
        user_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None,
        success: bool = True,
        error_message: Optional[str] = None,
    ) -> AuditLogEntry:
        """Create an audit log entry"""
        if not self._enabled:
            return None

        entry = AuditLogEntry(
            user_id=user_id,
            action=action,
            level=level,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id,
            request_id=request_id,
            success=success,
            error_message=error_message,
        )

        # Store entry
        self._logs[entry.id] = entry

        # Update indexes
        if user_id:
            if user_id not in self._user_index:
                self._user_index[user_id] = set()
            self._user_index[user_id].add(entry.id)

        if action not in self._action_index:
            self._action_index[action] = set()
        self._action_index[action].add(entry.id)

        return entry

    # Convenience methods
    def log_api_call(
        self, endpoint: str, method: str, user_id: Optional[str] = None, **kwargs
    ) -> AuditLogEntry:
        """Log an API call"""
        return self.log(
            action=AuditAction.API_CALL,
            user_id=user_id,
            resource_type="api",
            resource_id=endpoint,
            details={"method": method, "endpoint": endpoint},
            **kwargs,
        )

    def log_browser_action(
        self, action_type: str, tab_id: int, user_id: Optional[str] = None, **kwargs
    ) -> AuditLogEntry:
        """Log a browser action"""
        return self.log(
            action=AuditAction.ACTION_EXECUTED,
            user_id=user_id,
            resource_type="browser",
            resource_id=str(tab_id),
            details={"action_type": action_type, "tab_id": tab_id},
            **kwargs,
        )

    def log_llm_request(
        self, model: str, provider: str, tokens_used: int, user_id: Optional[str] = None, **kwargs
    ) -> AuditLogEntry:
        """Log an LLM request"""
        return self.log(
            action=AuditAction.LLM_REQUEST,
            user_id=user_id,
            resource_type="llm",
            resource_id=model,
            details={"model": model, "provider": provider, "tokens_used": tokens_used},
            **kwargs,
        )

    # ============== Querying ==============

    def get_log(self, log_id: str) -> Optional[AuditLogEntry]:
        """Get a specific log entry"""
        return self._logs.get(log_id)

    def get_logs(
        self,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        level: Optional[AuditLevel] = None,
        resource_type: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        success: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[AuditLogEntry]:
        """Get audit logs with filtering"""
        results = list(self._logs.values())

        # Filter by user
        if user_id:
            results = [l for l in results if l.user_id == user_id]

        # Filter by action
        if action:
            results = [l for l in results if l.action == action]

        # Filter by level
        if level:
            results = [l for l in results if l.level == level]

        # Filter by resource type
        if resource_type:
            results = [l for l in results if l.resource_type == resource_type]

        # Filter by date range
        if start_date:
            results = [l for l in results if l.timestamp >= start_date]

        if end_date:
            results = [l for l in results if l.timestamp <= end_date]

        # Filter by success
        if success is not None:
            results = [l for l in results if l.success == success]

        # Sort by timestamp
        results.sort(key=lambda l: l.timestamp, reverse=True)

        return results[offset : offset + limit]

    def search(self, query: str, limit: int = 50) -> List[AuditLogEntry]:
        """Search audit logs"""
        query_lower = query.lower()
        results = []

        for log in self._logs.values():
            # Search in details, resource_id, error_message
            searchable = " ".join(
                [json.dumps(log.details), log.resource_id or "", log.error_message or ""]
            ).lower()

            if query_lower in searchable:
                results.append(log)

        results.sort(key=lambda l: l.timestamp, reverse=True)
        return results[:limit]

    # ============== Statistics ==============

    def get_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get audit log statistics"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        recent_logs = [l for l in self._logs.values() if l.timestamp >= cutoff]

        # Count by action
        action_counts: Dict[str, int] = {}
        for log in recent_logs:
            action = log.action.value
            action_counts[action] = action_counts.get(action, 0) + 1

        # Count by level
        level_counts: Dict[str, int] = {}
        for log in recent_logs:
            level = log.level.value
            level_counts[level] = level_counts.get(level, 0) + 1

        # Count by user
        user_counts: Dict[str, int] = {}
        for log in recent_logs:
            if log.user_id:
                user_counts[log.user_id] = user_counts.get(log.user_id, 0) + 1

        # Failed actions
        failed_count = sum(1 for l in recent_logs if not l.success)

        return {
            "total_logs": len(self._logs),
            "logs_last_days": days,
            "recent_logs": len(recent_logs),
            "by_action": action_counts,
            "by_level": level_counts,
            "by_user": user_counts,
            "failed_count": failed_count,
            "success_rate": (len(recent_logs) - failed_count) / max(len(recent_logs), 1),
        }

    def get_user_activity(self, user_id: str, days: int = 30) -> List[AuditLogEntry]:
        """Get activity for a specific user"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        logs = [l for l in self._logs.values() if l.user_id == user_id and l.timestamp >= cutoff]

        logs.sort(key=lambda l: l.timestamp, reverse=True)
        return logs

    # ============== Export ==============

    def export_logs(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        format: str = "json",
    ) -> str:
        """Export audit logs"""
        logs = self.get_logs(start_date=start_date, end_date=end_date, limit=100000)

        if format == "json":
            return json.dumps([l.to_dict() for l in logs], indent=2)

        # CSV format
        if format == "csv":
            lines = ["timestamp,user_id,action,level,resource_type,success"]
            for log in logs:
                lines.append(
                    f"{log.timestamp.isoformat()},"
                    f"{log.user_id or ''},"
                    f"{log.action.value},"
                    f"{log.level.value},"
                    f"{log.resource_type or ''},"
                    f"{log.success}"
                )
            return "\n".join(lines)

        return str(logs)

    # ============== Retention ==============

    def set_retention(self, days: int) -> None:
        """Set retention period in days"""
        self._retention_days = days

    def get_retention(self) -> int:
        """Get retention period in days"""
        return self._retention_days

    def cleanup_old_logs(self) -> int:
        """Delete logs older than retention period"""
        cutoff = datetime.utcnow() - timedelta(days=self._retention_days)

        to_delete = [log_id for log_id, log in self._logs.items() if log.timestamp < cutoff]

        for log_id in to_delete:
            del self._logs[log_id]

        return len(to_delete)

    # ============== Configuration ==============

    def enable(self) -> None:
        """Enable audit logging"""
        self._enabled = True

    def disable(self) -> None:
        """Disable audit logging"""
        self._enabled = False

    def is_enabled(self) -> bool:
        """Check if audit logging is enabled"""
        return self._enabled


# Singleton
_audit_service: Optional[AuditLogService] = None


def get_audit_service() -> AuditLogService:
    """Get the audit log service instance"""
    global _audit_service
    if _audit_service is None:
        _audit_service = AuditLogService()
    return _audit_service
