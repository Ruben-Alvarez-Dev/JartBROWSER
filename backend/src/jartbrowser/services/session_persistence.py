"""
Session Persistence Service

Provides session management, save/restore functionality,
and automatic session persistence.
"""

import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import asyncio


@dataclass
class SessionData:
    """Session data"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    tabs: List[Dict[str, Any]] = field(default_factory=list)
    window_state: Dict[str, Any] = field(default_factory=dict)
    cookies: List[Dict[str, Any]] = field(default_factory=list)
    local_storage: Dict[str, Any] = field(default_factory=dict)
    session_storage: Dict[str, Any] = field(default_factory=dict)
    scroll_positions: Dict[str, int] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "tabs": self.tabs,
            "window_state": self.window_state,
            "cookies": self.cookies,
            "local_storage": self.local_storage,
            "session_storage": self.session_storage,
            "scroll_positions": self.scroll_positions,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "metadata": self.metadata,
        }


class SessionPersistenceService:
    """
    Service for managing browser sessions.

    Provides:
    - Session save/restore
    - Auto-save functionality
    - Session metadata
    - Session templates
    """

    def __init__(self):
        self._sessions: Dict[str, SessionData] = {}
        self._auto_save_enabled: bool = False
        self._auto_save_interval_seconds: int = 300  # 5 minutes
        self._max_sessions: int = 50

    # ============== Session Management ==============

    async def create_session(
        self,
        name: str,
        tabs: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SessionData:
        """Create a new session"""
        session = SessionData(name=name, tabs=tabs or [], metadata=metadata or {})

        self._sessions[session.id] = session

        # Enforce max sessions
        await self._enforce_max_sessions()

        return session

    async def update_session(
        self,
        session_id: str,
        tabs: Optional[List[Dict[str, Any]]] = None,
        window_state: Optional[Dict[str, Any]] = None,
        cookies: Optional[List[Dict[str, Any]]] = None,
        scroll_positions: Optional[Dict[str, int]] = None,
    ) -> Optional[SessionData]:
        """Update session data"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        if tabs is not None:
            session.tabs = tabs
        if window_state is not None:
            session.window_state = window_state
        if cookies is not None:
            session.cookies = cookies
        if scroll_positions is not None:
            session.scroll_positions = scroll_positions

        session.updated_at = datetime.utcnow()

        return session

    def get_session(self, session_id: str) -> Optional[SessionData]:
        """Get a session"""
        return self._sessions.get(session_id)

    def get_sessions(self, limit: int = 20, offset: int = 0) -> List[SessionData]:
        """Get all sessions"""
        sessions = list(self._sessions.values())
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        return sessions[offset : offset + limit]

    async def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    # ============== Save/Restore ==============

    async def save_current_state(
        self,
        session_id: str,
        current_tabs: List[Dict[str, Any]],
        window_state: Dict[str, Any],
        cookies: Optional[List[Dict[str, Any]]] = None,
        scroll_positions: Optional[Dict[str, int]] = None,
    ) -> Optional[SessionData]:
        """Save current browser state to session"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        session.tabs = current_tabs
        session.window_state = window_state
        if cookies:
            session.cookies = cookies
        if scroll_positions:
            session.scroll_positions = scroll_positions

        session.updated_at = datetime.utcnow()

        return session

    async def get_session_tabs(self, session_id: str) -> Optional[List[Dict[str, Any]]]:
        """Get tabs from session"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return session.tabs

    async def get_session_window_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get window state from session"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return session.window_state

    # ============== Auto-Save ==============

    def enable_auto_save(self, interval_seconds: int = 300) -> None:
        """Enable auto-save"""
        self._auto_save_enabled = True
        self._auto_save_interval_seconds = interval_seconds

    def disable_auto_save(self) -> None:
        """Disable auto-save"""
        self._auto_save_enabled = False

    def is_auto_save_enabled(self) -> bool:
        """Check if auto-save is enabled"""
        return self._auto_save_enabled

    def get_auto_save_interval(self) -> int:
        """Get auto-save interval in seconds"""
        return self._auto_save_interval_seconds

    # ============== Import/Export ==============

    async def export_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Export session as JSON"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        return session.to_dict()

    async def import_session(
        self, session_data: Dict[str, Any], merge: bool = False
    ) -> SessionData:
        """Import session from JSON"""
        if merge:
            # Check if session exists
            existing = self._sessions.get(session_data.get("id"))
            if existing:
                # Update existing
                return await self.update_session(
                    existing.id,
                    tabs=session_data.get("tabs"),
                    window_state=session_data.get("window_state"),
                    cookies=session_data.get("cookies"),
                )

        # Create new session
        session = SessionData(
            id=session_data.get("id", str(uuid.uuid4())),
            name=session_data.get("name", "Imported Session"),
            tabs=session_data.get("tabs", []),
            window_state=session_data.get("window_state", {}),
            cookies=session_data.get("cookies", []),
            local_storage=session_data.get("local_storage", {}),
            session_storage=session_data.get("session_storage", {}),
            scroll_positions=session_data.get("scroll_positions", {}),
            metadata=session_data.get("metadata", {}),
        )

        self._sessions[session.id] = session
        return session

    # ============== Cleanup ==============

    async def _enforce_max_sessions(self) -> None:
        """Enforce maximum number of sessions"""
        if len(self._sessions) > self._max_sessions:
            # Remove oldest sessions
            sorted_sessions = sorted(self._sessions.values(), key=lambda s: s.updated_at)

            to_remove = len(self._sessions) - self._max_sessions
            for session in sorted_sessions[:to_remove]:
                del self._sessions[session.id]

    async def delete_old_sessions(self, days: int) -> int:
        """Delete sessions older than N days"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        to_delete = [s.id for s in self._sessions.values() if s.updated_at < cutoff]

        for session_id in to_delete:
            del self._sessions[session_id]

        return len(to_delete)

    # ============== Statistics ==============

    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics"""
        total_tabs = sum(len(s.tabs) for s in self._sessions.values())

        return {
            "total_sessions": len(self._sessions),
            "total_tabs": total_tabs,
            "auto_save_enabled": self._auto_save_enabled,
            "auto_save_interval": self._auto_save_interval_seconds,
            "max_sessions": self._max_sessions,
        }


# Singleton
_session_service: Optional[SessionPersistenceService] = None


def get_session_service() -> SessionPersistenceService:
    """Get the session persistence service instance"""
    global _session_service
    if _session_service is None:
        _session_service = SessionPersistenceService()
    return _session_service
