"""
Multi-Tab Coordination Service

Provides coordination capabilities across multiple tabs,
including state synchronization, cross-tab messaging, and parallel agent execution.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
import json


class CoordinationEvent(Enum):
    """Cross-tab coordination events"""

    TAB_UPDATED = "tab_updated"
    TAB_CLOSED = "tab_closed"
    STATE_CHANGED = "state_changed"
    MESSAGE_SENT = "message_sent"
    AGENT_STARTED = "agent_started"
    AGENT_STOPPED = "agent_stopped"
    ACTION_EXECUTED = "action_executed"


@dataclass
class CrossTabMessage:
    """Message sent between tabs"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    source_tab_id: int = 0
    target_tab_id: Optional[int] = None  # None = broadcast
    event: CoordinationEvent = CoordinationEvent.MESSAGE_SENT
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class TabState:
    """State of a tab"""

    tab_id: int
    url: str
    title: str
    last_active: datetime = field(default_factory=datetime.utcnow)
    custom_data: Dict[str, Any] = field(default_factory=dict)
    agent_running: bool = False


@dataclass
class AgentTask:
    """Agent task running on tabs"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = ""
    target_tabs: List[int] = field(default_factory=list)
    status: str = "pending"  # pending, running, completed, failed
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class MultiTabCoordinationService:
    """
    Service for coordinating actions across multiple tabs.

    Provides:
    - Cross-tab messaging
    - State synchronization
    - Parallel agent execution
    - Event coordination
    """

    def __init__(self):
        self._tab_states: Dict[int, TabState] = {}
        self._messages: List[CrossTabMessage] = []
        self._agents: Dict[str, AgentTask] = {}
        self._event_handlers: Dict[CoordinationEvent, List[Callable]] = {}
        self._sync_enabled: bool = True

    # ============== Tab State Management ==============

    async def register_tab(self, tab_id: int, url: str, title: str) -> TabState:
        """Register a new tab"""
        state = TabState(tab_id=tab_id, url=url, title=title)
        self._tab_states[tab_id] = state

        # Notify handlers
        await self._emit_event(
            CoordinationEvent.TAB_UPDATED, {"tab_id": tab_id, "action": "registered"}
        )

        return state

    async def unregister_tab(self, tab_id: int) -> bool:
        """Unregister a tab"""
        if tab_id in self._tab_states:
            del self._tab_states[tab_id]

            # Notify handlers
            await self._emit_event(CoordinationEvent.TAB_CLOSED, {"tab_id": tab_id})

            return True
        return False

    async def update_tab_state(
        self,
        tab_id: int,
        url: Optional[str] = None,
        title: Optional[str] = None,
        custom_data: Optional[Dict[str, Any]] = None,
    ) -> Optional[TabState]:
        """Update tab state"""
        state = self._tab_states.get(tab_id)
        if not state:
            return None

        if url is not None:
            state.url = url
        if title is not None:
            state.title = title
        if custom_data is not None:
            state.custom_data.update(custom_data)

        state.last_active = datetime.utcnow()

        # Notify handlers
        if self._sync_enabled:
            await self._emit_event(
                CoordinationEvent.STATE_CHANGED, {"tab_id": tab_id, "state": state.custom_data}
            )

        return state

    def get_tab_state(self, tab_id: int) -> Optional[TabState]:
        """Get state of a specific tab"""
        return self._tab_states.get(tab_id)

    def get_all_tab_states(self) -> List[TabState]:
        """Get all tab states"""
        return list(self._tab_states.values())

    # ============== Cross-Tab Messaging ==============

    async def send_message(
        self,
        source_tab_id: int,
        target_tab_id: Optional[int],
        event: CoordinationEvent,
        payload: Dict[str, Any],
    ) -> CrossTabMessage:
        """Send a message between tabs"""
        message = CrossTabMessage(
            source_tab_id=source_tab_id, target_tab_id=target_tab_id, event=event, payload=payload
        )

        self._messages.append(message)

        # Emit event for handlers
        await self._emit_event(CoordinationEvent.MESSAGE_SENT, {"message": message.to_dict()})

        return message

    async def broadcast(
        self, source_tab_id: int, event: CoordinationEvent, payload: Dict[str, Any]
    ) -> List[CrossTabMessage]:
        """Broadcast to all tabs"""
        messages = []

        for tab_id in self._tab_states.keys():
            if tab_id != source_tab_id:
                msg = await self.send_message(
                    source_tab_id=source_tab_id, target_tab_id=tab_id, event=event, payload=payload
                )
                messages.append(msg)

        return messages

    def get_messages(self, tab_id: Optional[int] = None, limit: int = 50) -> List[CrossTabMessage]:
        """Get messages for a tab"""
        messages = self._messages

        if tab_id is not None:
            messages = [m for m in messages if m.target_tab_id == tab_id or m.target_tab_id is None]

        return messages[-limit:]

    # ============== State Synchronization ==============

    def enable_sync(self) -> None:
        """Enable state synchronization"""
        self._sync_enabled = True

    def disable_sync(self) -> None:
        """Disable state synchronization"""
        self._sync_enabled = False

    async def sync_state(self, source_tab_id: int, state_key: str, state_value: Any) -> None:
        """Sync state to all other tabs"""
        if not self._sync_enabled:
            return

        payload = {"key": state_key, "value": state_value, "source_tab": source_tab_id}

        await self.broadcast(
            source_tab_id=source_tab_id, event=CoordinationEvent.STATE_CHANGED, payload=payload
        )

    async def get_shared_state(self, key: str) -> Dict[int, Any]:
        """Get shared state from all tabs"""
        shared = {}

        for tab_id, state in self._tab_states.items():
            if key in state.custom_data:
                shared[tab_id] = state.custom_data[key]

        return shared

    # ============== Parallel Agent Execution ==============

    async def start_agent(self, task_type: str, target_tabs: List[int]) -> AgentTask:
        """Start an agent task on multiple tabs"""
        task = AgentTask(
            task_type=task_type,
            target_tabs=target_tabs,
            status="running",
            started_at=datetime.utcnow(),
        )

        self._agents[task.id] = task

        # Mark tabs as having running agent
        for tab_id in target_tabs:
            if tab_id in self._tab_states:
                self._tab_states[tab_id].agent_running = True

        # Emit event
        await self._emit_event(
            CoordinationEvent.AGENT_STARTED, {"task_id": task.id, "tabs": target_tabs}
        )

        return task

    async def update_agent_progress(self, task_id: str, progress: float) -> Optional[AgentTask]:
        """Update agent progress"""
        task = self._agents.get(task_id)
        if not task:
            return None

        task.progress = progress
        return task

    async def complete_agent(self, task_id: str, result: Dict[str, Any]) -> Optional[AgentTask]:
        """Complete an agent task"""
        task = self._agents.get(task_id)
        if not task:
            return None

        task.status = "completed"
        task.progress = 1.0
        task.result = result
        task.completed_at = datetime.utcnow()

        # Clear agent running flag from tabs
        for tab_id in task.target_tabs:
            if tab_id in self._tab_states:
                self._tab_states[tab_id].agent_running = False

        # Emit event
        await self._emit_event(
            CoordinationEvent.AGENT_STOPPED, {"task_id": task_id, "status": "completed"}
        )

        return task

    async def fail_agent(self, task_id: str, error: str) -> Optional[AgentTask]:
        """Fail an agent task"""
        task = self._agents.get(task_id)
        if not task:
            return None

        task.status = "failed"
        task.error = error
        task.completed_at = datetime.utcnow()

        # Clear agent running flag from tabs
        for tab_id in task.target_tabs:
            if tab_id in self._tab_states:
                self._tab_states[tab_id].agent_running = False

        # Emit event
        await self._emit_event(
            CoordinationEvent.AGENT_STOPPED,
            {"task_id": task_id, "status": "failed", "error": error},
        )

        return task

    def get_agent(self, task_id: str) -> Optional[AgentTask]:
        """Get agent task"""
        return self._agents.get(task_id)

    def get_running_agents(self) -> List[AgentTask]:
        """Get all running agents"""
        return [a for a in self._agents.values() if a.status == "running"]

    def get_agent_history(self, tab_id: Optional[int] = None, limit: int = 50) -> List[AgentTask]:
        """Get agent task history"""
        tasks = list(self._agents.values())

        if tab_id is not None:
            tasks = [t for t in tasks if tab_id in t.target_tabs]

        tasks.sort(key=lambda t: t.created_at, reverse=True)
        return tasks[:limit]

    # ============== Event Handlers ==============

    def on_event(self, event: CoordinationEvent, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Register an event handler"""
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(handler)

    def off_event(self, event: CoordinationEvent, handler: Callable[[Dict[str, Any]], Any]) -> None:
        """Unregister an event handler"""
        if event in self._event_handlers:
            if handler in self._event_handlers[event]:
                self._event_handlers[event].remove(handler)

    async def _emit_event(self, event: CoordinationEvent, data: Dict[str, Any]) -> None:
        """Emit an event to all handlers"""
        if event in self._event_handlers:
            for handler in self._event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        await handler(data)
                    else:
                        handler(data)
                except Exception:
                    pass

    # ============== Statistics ==============

    def get_stats(self) -> Dict[str, Any]:
        """Get coordination statistics"""
        running_agents = len(self.get_running_agents())

        return {
            "total_tabs": len(self._tab_states),
            "running_agents": running_agents,
            "total_messages": len(self._messages),
            "total_agents": len(self._agents),
            "sync_enabled": self._sync_enabled,
        }


# Helper for message serialization
def cross_tab_message_to_dict(msg: CrossTabMessage) -> Dict[str, Any]:
    return {
        "id": msg.id,
        "source_tab_id": msg.source_tab_id,
        "target_tab_id": msg.target_tab_id,
        "event": msg.event.value,
        "payload": msg.payload,
        "timestamp": msg.timestamp.isoformat(),
    }


# Singleton
_coordination_service: Optional[MultiTabCoordinationService] = None


def get_coordination_service() -> MultiTabCoordinationService:
    """Get the coordination service instance"""
    global _coordination_service
    if _coordination_service is None:
        _coordination_service = MultiTabCoordinationService()
    return _coordination_service
