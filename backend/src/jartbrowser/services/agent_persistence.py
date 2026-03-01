"""
Agent Persistence & Recovery Service

Provides agent state persistence, recovery, and checkpoint management.
"""

import uuid
import json
import asyncio
import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
from pathlib import Path
import pickle
import gzip


class AgentState(Enum):
    """Agent state"""

    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"
    RECOVERING = "recovering"
    TERMINATED = "terminated"


class RecoveryPoint(Enum):
    """Recovery point type"""

    MANUAL = "manual"
    AUTOMATIC = "automatic"
    ERROR = "error"
    TIMEOUT = "timeout"


class RecoveryStatus(Enum):
    """Recovery status"""

    NONE = "none"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class AgentCheckpoint:
    """Agent checkpoint for recovery"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    state: AgentState = AgentState.IDLE
    checkpoint_type: RecoveryPoint = RecoveryPoint.AUTOMATIC
    state_data: Dict[str, Any] = field(default_factory=dict)
    execution_context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "state": self.state.value,
            "checkpoint_type": self.checkpoint_type.value,
            "state_data": self.state_data,
            "execution_context": self.execution_context,
            "stack_trace": self.stack_trace,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata,
            "checksum": self.checksum,
        }


@dataclass
class AgentSession:
    """Agent session with persistence"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str = ""
    name: str = ""
    state: AgentState = AgentState.IDLE
    current_task: Optional[str] = None
    state_data: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    variables: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict[str, Any]] = field(default_factory=list)
    checkpoints: List[str] = field(default_factory=list)  # checkpoint IDs
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    last_checkpoint: Optional[datetime] = None
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "name": self.name,
            "state": self.state.value,
            "current_task": self.current_task,
            "state_data": self.state_data,
            "context": self.context,
            "variables": self.variables,
            "history": self.history,
            "checkpoints": self.checkpoints,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_checkpoint": self.last_checkpoint.isoformat() if self.last_checkpoint else None,
            "recovery_attempts": self.recovery_attempts,
            "max_recovery_attempts": self.max_recovery_attempts,
            "metadata": self.metadata,
        }


@dataclass
class RecoveryResult:
    """Recovery result"""

    success: bool
    status: RecoveryStatus
    session: Optional[AgentSession] = None
    checkpoint: Optional[AgentCheckpoint] = None
    restored_variables: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    recovered_state: Optional[Dict[str, Any]] = None


class AgentPersistenceService:
    """
    Service for agent persistence and recovery.

    Provides:
    - Agent state persistence
    - Automatic and manual checkpoints
    - Session recovery
    - State restoration
    - Crash recovery
    """

    def __init__(self, storage_path: Optional[str] = None):
        self._sessions: Dict[str, AgentSession] = {}
        self._checkpoints: Dict[str, AgentCheckpoint] = {}
        self._storage_path = storage_path
        self._auto_checkpoint_interval = 300  # 5 minutes
        self._max_checkpoints_per_agent = 10
        self._recovery_handlers: Dict[str, Callable[[AgentSession], Awaitable[Dict[str, Any]]]] = {}
        self._state_change_handlers: Dict[str, Callable[[AgentSession, AgentState], None]] = {}

    def set_storage_path(self, path: str) -> None:
        """Set storage path for persistence"""
        self._storage_path = path
        Path(path).mkdir(parents=True, exist_ok=True)

    def register_recovery_handler(
        self, agent_type: str, handler: Callable[[AgentSession], Awaitable[Dict[str, Any]]]
    ) -> None:
        """Register a recovery handler for an agent type"""
        self._recovery_handlers[agent_type] = handler

    def register_state_change_handler(
        self, handler: Callable[[AgentSession, AgentState], None]
    ) -> None:
        """Register a state change handler"""
        self._state_change_handlers[id(handler)] = handler

    # ============== Session Management ==============

    def create_session(
        self,
        agent_id: str,
        name: str,
        initial_state: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        max_recovery_attempts: int = 3,
    ) -> AgentSession:
        """Create a new agent session"""
        session = AgentSession(
            agent_id=agent_id,
            name=name,
            state=AgentState.IDLE,
            state_data=initial_state or {},
            context=context or {},
            max_recovery_attempts=max_recovery_attempts,
        )
        self._sessions[session.id] = session

        # Create initial checkpoint
        self._create_checkpoint(session, RecoveryPoint.MANUAL, "Initial state")

        return session

    def get_session(self, session_id: str) -> Optional[AgentSession]:
        """Get a session"""
        return self._sessions.get(session_id)

    def get_sessions(
        self,
        agent_id: Optional[str] = None,
        state: Optional[AgentState] = None,
        limit: int = 50,
    ) -> List[AgentSession]:
        """Get sessions"""
        results = list(self._sessions.values())

        if agent_id:
            results = [s for s in results if s.agent_id == agent_id]
        if state:
            results = [s for s in results if s.state == state]

        results.sort(key=lambda s: s.updated_at, reverse=True)
        return results[:limit]

    def update_session(
        self,
        session_id: str,
        state: Optional[AgentState] = None,
        current_task: Optional[str] = None,
        state_data: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
    ) -> Optional[AgentSession]:
        """Update session state"""
        session = self._sessions.get(session_id)
        if not session:
            return None

        old_state = session.state

        if state is not None:
            session.state = state
        if current_task is not None:
            session.current_task = current_task
        if state_data is not None:
            session.state_data.update(state_data)
        if context is not None:
            session.context.update(context)
        if variables is not None:
            session.variables.update(variables)

        session.updated_at = datetime.utcnow()

        # Trigger state change handlers
        if old_state != session.state:
            for handler in self._state_change_handlers.values():
                try:
                    handler(session, old_state)
                except Exception:
                    pass

        return session

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        if session_id in self._sessions:
            # Delete associated checkpoints
            session = self._sessions[session_id]
            for checkpoint_id in session.checkpoints:
                if checkpoint_id in self._checkpoints:
                    del self._checkpoints[checkpoint_id]
            del self._sessions[session_id]
            return True
        return False

    def add_history_entry(self, session_id: str, entry: Dict[str, Any]) -> bool:
        """Add an entry to session history"""
        session = self._sessions.get(session_id)
        if not session:
            return False

        entry["timestamp"] = datetime.utcnow().isoformat()
        session.history.append(entry)

        # Keep only last 1000 entries
        if len(session.history) > 1000:
            session.history = session.history[-1000:]

        session.updated_at = datetime.utcnow()
        return True

    # ============== Checkpoints ==============

    def _create_checkpoint(
        self,
        session: AgentSession,
        checkpoint_type: RecoveryPoint,
        description: str = "",
    ) -> AgentCheckpoint:
        """Create a checkpoint"""
        # Serialize state data
        state_data = json.dumps(session.state_data, sort_keys=True)
        context_data = json.dumps(session.context, sort_keys=True)

        checkpoint = AgentCheckpoint(
            agent_id=session.agent_id,
            state=session.state,
            checkpoint_type=checkpoint_type,
            state_data=session.state_data.copy(),
            execution_context=session.context.copy(),
            metadata={
                "session_id": session.id,
                "description": description,
                "variables_count": len(session.variables),
                "history_length": len(session.history),
            },
        )

        # Calculate checksum
        checkpoint.checksum = hashlib.sha256((state_data + context_data).encode()).hexdigest()

        self._checkpoints[checkpoint.id] = checkpoint
        session.checkpoints.append(checkpoint.id)
        session.last_checkpoint = datetime.utcnow()

        # Limit checkpoints per agent
        if len(session.checkpoints) > self._max_checkpoints_per_agent:
            old_id = session.checkpoints.pop(0)
            if old_id in self._checkpoints:
                del self._checkpoints[old_id]

        return checkpoint

    def create_checkpoint(
        self,
        session_id: str,
        checkpoint_type: RecoveryPoint = RecoveryPoint.MANUAL,
        description: str = "",
    ) -> Optional[AgentCheckpoint]:
        """Create a checkpoint for a session"""
        session = self._sessions.get(session_id)
        if not session:
            return None
        return self._create_checkpoint(session, checkpoint_type, description)

    def get_checkpoint(self, checkpoint_id: str) -> Optional[AgentCheckpoint]:
        """Get a checkpoint"""
        return self._checkpoints.get(checkpoint_id)

    def get_checkpoints(
        self,
        session_id: Optional[str] = None,
        checkpoint_type: Optional[RecoveryPoint] = None,
        limit: int = 20,
    ) -> List[AgentCheckpoint]:
        """Get checkpoints"""
        results = list(self._checkpoints.values())

        if session_id:
            results = [c for c in results if c.metadata.get("session_id") == session_id]
        if checkpoint_type:
            results = [c for c in results if c.checkpoint_type == checkpoint_type]

        results.sort(key=lambda c: c.created_at, reverse=True)
        return results[:limit]

    def get_latest_checkpoint(self, session_id: str) -> Optional[AgentCheckpoint]:
        """Get the latest checkpoint for a session"""
        session = self._sessions.get(session_id)
        if not session or not session.checkpoints:
            return None
        latest_id = session.checkpoints[-1]
        return self._checkpoints.get(latest_id)

    # ============== Recovery ==============

    async def recover_session(
        self,
        session_id: str,
        checkpoint_id: Optional[str] = None,
    ) -> RecoveryResult:
        """Recover a session from checkpoint"""
        session = self._sessions.get(session_id)
        if not session:
            return RecoveryResult(
                success=False,
                status=RecoveryStatus.FAILED,
                error="Session not found",
            )

        # Determine checkpoint to use
        checkpoint = None
        if checkpoint_id:
            checkpoint = self._checkpoints.get(checkpoint_id)
        else:
            checkpoint = self.get_latest_checkpoint(session_id)

        if not checkpoint:
            return RecoveryResult(
                success=False,
                status=RecoveryStatus.FAILED,
                error="No checkpoint available",
            )

        # Verify checkpoint integrity
        state_data = json.dumps(checkpoint.state_data, sort_keys=True)
        context_data = json.dumps(checkpoint.execution_context, sort_keys=True)
        expected_checksum = hashlib.sha256((state_data + context_data).encode()).hexdigest()

        if checkpoint.checksum != expected_checksum:
            return RecoveryResult(
                success=False,
                status=RecoveryStatus.FAILED,
                error="Checkpoint checksum mismatch - data may be corrupted",
            )

        # Perform recovery
        session.recovery_attempts += 1
        session.state = AgentState.RECOVERING
        session.updated_at = datetime.utcnow()

        try:
            # Restore state
            session.state_data = checkpoint.state_data.copy()
            session.context = checkpoint.execution_context.copy()
            session.state = AgentState.IDLE

            # Call recovery handler if registered
            handler = self._recovery_handlers.get(session.metadata.get("agent_type"))
            if handler:
                recovered_data = await handler(session)

            session.updated_at = datetime.utcnow()

            return RecoveryResult(
                success=True,
                status=RecoveryStatus.SUCCESS,
                session=session,
                checkpoint=checkpoint,
                restored_variables=checkpoint.state_data.copy(),
                recovered_state=checkpoint.execution_context.copy(),
            )

        except Exception as e:
            session.state = AgentState.IDLE
            session.updated_at = datetime.utcnow()

            if session.recovery_attempts >= session.max_recovery_attempts:
                return RecoveryResult(
                    success=False,
                    status=RecoveryStatus.FAILED,
                    session=session,
                    error=f"Max recovery attempts reached: {str(e)}",
                )

            return RecoveryResult(
                success=False,
                status=RecoveryStatus.PARTIAL,
                session=session,
                error=str(e),
            )

    async def auto_recover(self, agent_id: str) -> List[RecoveryResult]:
        """Attempt auto-recovery for all sessions of an agent"""
        sessions = self.get_sessions(agent_id=agent_id)
        results = []

        for session in sessions:
            if session.recovery_attempts < session.max_recovery_attempts:
                result = await self.recover_session(session.id)
                results.append(result)

        return results

    # ============== Persistence ==============

    async def save_to_disk(self) -> bool:
        """Save all sessions and checkpoints to disk"""
        if not self._storage_path:
            return False

        try:
            path = Path(self._storage_path)
            path.mkdir(parents=True, exist_ok=True)

            # Save sessions
            sessions_data = {sid: session.to_dict() for sid, session in self._sessions.items()}

            with open(path / "sessions.json", "w") as f:
                json.dump(sessions_data, f, indent=2)

            # Save checkpoints (compressed)
            checkpoints_data = {
                cid: checkpoint.to_dict() for cid, checkpoint in self._checkpoints.items()
            }

            with gzip.open(path / "checkpoints.json.gz", "wt") as f:
                json.dump(checkpoints_data, f)

            return True
        except Exception:
            return False

    async def load_from_disk(self) -> bool:
        """Load sessions and checkpoints from disk"""
        if not self._storage_path:
            return False

        try:
            path = Path(self._storage_path)
            if not path.exists():
                return False

            # Load sessions
            sessions_file = path / "sessions.json"
            if sessions_file.exists():
                with open(sessions_file, "r") as f:
                    sessions_data = json.load(f)

                for sid, data in sessions_data.items():
                    session = AgentSession(
                        id=data["id"],
                        agent_id=data["agent_id"],
                        name=data["name"],
                        state=AgentState(data["state"]),
                        current_task=data.get("current_task"),
                        state_data=data.get("state_data", {}),
                        context=data.get("context", {}),
                        variables=data.get("variables", {}),
                        history=data.get("history", []),
                        checkpoints=data.get("checkpoints", []),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        updated_at=datetime.fromisoformat(data["updated_at"]),
                        last_checkpoint=datetime.fromisoformat(data["last_checkpoint"])
                        if data.get("last_checkpoint")
                        else None,
                        recovery_attempts=data.get("recovery_attempts", 0),
                        max_recovery_attempts=data.get("max_recovery_attempts", 3),
                        metadata=data.get("metadata", {}),
                    )
                    self._sessions[sid] = session

            # Load checkpoints
            checkpoints_file = path / "checkpoints.json.gz"
            if checkpoints_file.exists():
                with gzip.open(checkpoints_file, "rt") as f:
                    checkpoints_data = json.load(f)

                for cid, data in checkpoints_data.items():
                    checkpoint = AgentCheckpoint(
                        id=data["id"],
                        agent_id=data["agent_id"],
                        state=AgentState(data["state"]),
                        checkpoint_type=RecoveryPoint(data["checkpoint_type"]),
                        state_data=data.get("state_data", {}),
                        execution_context=data.get("execution_context", {}),
                        stack_trace=data.get("stack_trace"),
                        created_at=datetime.fromisoformat(data["created_at"]),
                        metadata=data.get("metadata", {}),
                        checksum=data.get("checksum", ""),
                    )
                    self._checkpoints[cid] = checkpoint

            return True
        except Exception:
            return False


# Singleton
_agent_persistence: Optional[AgentPersistenceService] = None


def get_agent_persistence() -> AgentPersistenceService:
    """Get the agent persistence service instance"""
    global _agent_persistence
    if _agent_persistence is None:
        _agent_persistence = AgentPersistenceService()
    return _agent_persistence
