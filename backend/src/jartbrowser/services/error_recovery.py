"""
Error Recovery & Self-Healing Service

Provides error detection, recovery strategies, and self-healing capabilities.
"""

import uuid
import asyncio
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Awaitable
from enum import Enum
from collections import defaultdict
import logging


class ErrorSeverity(Enum):
    """Error severity levels"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories"""

    NETWORK = "network"
    TIMEOUT = "timeout"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    RESOURCE = "resource"
    VALIDATION = "validation"
    RATE_LIMIT = "rate_limit"
    EXTERNAL_SERVICE = "external_service"
    INTERNAL = "internal"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategies"""

    RETRY = "retry"
    FALLBACK = "fallback"
    CIRCUIT_BREAK = "circuit_break"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ESCALATE = "escalate"
    SELF_HEAL = "self_heal"


class CircuitState(Enum):
    """Circuit breaker states"""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class ErrorRecord:
    """Error record for analysis"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_type: str = ""
    message: str = ""
    category: ErrorCategory = ErrorCategory.UNKNOWN
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    service: str = ""
    operation: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    stack_trace: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    resolved: bool = False
    resolution: Optional[str] = None
    resolution_timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CircuitBreaker:
    """Circuit breaker for service protection"""

    name: str = ""
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout: int = 60  # seconds
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[datetime] = None
    last_state_change: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "failureCount": self.failure_count,
            "successCount": self.success_count,
            "lastFailureTime": self.last_failure_time.isoformat()
            if self.last_failure_time
            else None,
            "lastStateChange": self.last_state_change.isoformat(),
        }


@dataclass
class RecoveryAction:
    """Recovery action"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    error_id: str = ""
    strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    action_type: str = ""
    action_data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, running, success, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


@dataclass
class SelfHealingRule:
    """Self-healing rule"""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    error_pattern: str = ""  # Regex pattern
    error_category: Optional[ErrorCategory] = None
    severity_threshold: ErrorSeverity = ErrorSeverity.MEDIUM
    actions: List[Dict[str, Any]] = field(default_factory=list)
    enabled: bool = True
    cooldown: int = 300  # seconds between executions
    last_executed: Optional[datetime] = None
    execution_count: int = 0
    success_count: int = 0


class ErrorRecoveryService:
    """
    Service for error recovery and self-healing.

    Provides:
    - Error detection and classification
    - Automatic retry mechanisms
    - Circuit breaker pattern
    - Fallback strategies
    - Self-healing actions
    - Error analytics
    """

    def __init__(self):
        self._errors: Dict[str, ErrorRecord] = {}
        self._circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._recovery_actions: Dict[str, RecoveryAction] = {}
        self._self_healing_rules: Dict[str, SelfHealingRule] = {}
        self._retry_configs: Dict[str, Dict[str, Any]] = {}
        self._fallback_handlers: Dict[str, Callable] = {}
        self._error_handlers: Dict[ErrorCategory, Callable] = {}
        self._max_errors_per_service = 1000
        self._logger = logging.getLogger(__name__)

        # Default retry configuration
        self._default_retry_config = {
            "max_attempts": 3,
            "initial_delay": 1.0,
            "max_delay": 30.0,
            "backoff_multiplier": 2.0,
            "retry_on": [Exception],
        }

    # ============== Error Recording ==============

    def record_error(
        self,
        error: Exception,
        service: str,
        operation: str,
        category: ErrorCategory = ErrorCategory.UNKNOWN,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        context: Optional[Dict[str, Any]] = None,
    ) -> ErrorRecord:
        """Record an error"""
        error_type = type(error).__name__

        record = ErrorRecord(
            error_type=error_type,
            message=str(error),
            category=category,
            severity=severity,
            service=service,
            operation=operation,
            context=context or {},
            stack_trace=traceback.format_exc(),
        )

        self._errors[record.id] = record

        # Cleanup old errors
        self._cleanup_errors(service)

        # Trigger error handlers
        handler = self._error_handlers.get(category)
        if handler:
            try:
                handler(record)
            except Exception:
                pass

        # Check for self-healing
        asyncio.create_task(self._check_self_healing(record))

        return record

    def _cleanup_errors(self, service: str) -> None:
        """Cleanup old errors for a service"""
        service_errors = [e for e in self._errors.values() if e.service == service]

        if len(service_errors) > self._max_errors_per_service:
            # Keep most recent
            sorted_errors = sorted(service_errors, key=lambda e: e.timestamp, reverse=True)
            for error in sorted_errors[self._max_errors_per_service :]:
                del self._errors[error.id]

    def get_error(self, error_id: str) -> Optional[ErrorRecord]:
        """Get an error record"""
        return self._errors.get(error_id)

    def get_errors(
        self,
        service: Optional[str] = None,
        category: Optional[ErrorCategory] = None,
        severity: Optional[ErrorSeverity] = None,
        resolved: Optional[bool] = None,
        limit: int = 50,
    ) -> List[ErrorRecord]:
        """Get error records"""
        results = list(self._errors.values())

        if service:
            results = [e for e in results if e.service == service]
        if category:
            results = [e for e in results if e.category == category]
        if severity:
            results = [e for e in results if e.severity == severity]
        if resolved is not None:
            results = [e for e in results if e.resolved == resolved]

        results.sort(key=lambda e: e.timestamp, reverse=True)
        return results[:limit]

    def resolve_error(self, error_id: str, resolution: str) -> bool:
        """Mark error as resolved"""
        error = self._errors.get(error_id)
        if not error:
            return False

        error.resolved = True
        error.resolution = resolution
        error.resolution_timestamp = datetime.utcnow()
        return True

    # ============== Retry Mechanism ==============

    def configure_retry(
        self,
        operation: str,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 30.0,
        backoff_multiplier: float = 2.0,
        retry_on: Optional[List[type]] = None,
    ) -> None:
        """Configure retry for an operation"""
        self._retry_configs[operation] = {
            "max_attempts": max_attempts,
            "initial_delay": initial_delay,
            "max_delay": max_delay,
            "backoff_multiplier": backoff_multiplier,
            "retry_on": retry_on or [Exception],
        }

    async def execute_with_retry(
        self,
        operation: str,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with retry"""
        config = self._retry_configs.get(operation, self._default_retry_config)

        last_error = None
        delay = config["initial_delay"]

        for attempt in range(config["max_attempts"]):
            try:
                result = await func(*args, **kwargs)

                # Reset circuit breaker on success
                circuit = self._circuit_breakers.get(operation)
                if circuit:
                    self._record_circuit_success(operation)

                return result

            except Exception as e:
                last_error = e

                # Check if we should retry
                should_retry = any(isinstance(e, exc_type) for exc_type in config["retry_on"])

                if not should_retry or attempt == config["max_attempts"] - 1:
                    # Record failure
                    self._record_circuit_failure(operation)
                    raise

                # Record circuit breaker failure
                self._record_circuit_failure(operation)

                # Wait before retry
                await asyncio.sleep(delay)
                delay = min(delay * config["backoff_multiplier"], config["max_delay"])

        if last_error:
            raise last_error

    # ============== Circuit Breaker ==============

    def create_circuit_breaker(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 2,
        timeout: int = 60,
    ) -> CircuitBreaker:
        """Create a circuit breaker"""
        circuit = CircuitBreaker(
            name=name,
            failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            timeout=timeout,
        )
        self._circuit_breakers[name] = circuit
        return circuit

    def get_circuit_breaker(self, name: str) -> Optional[CircuitBreaker]:
        """Get a circuit breaker"""
        return self._circuit_breakers.get(name)

    def get_circuit_breakers(self) -> List[CircuitBreaker]:
        """Get all circuit breakers"""
        return list(self._circuit_breakers.values())

    def _record_circuit_failure(self, name: str) -> None:
        """Record circuit breaker failure"""
        circuit = self._circuit_breakers.get(name)
        if not circuit:
            return

        circuit.failure_count += 1
        circuit.last_failure_time = datetime.utcnow()

        if (
            circuit.state == CircuitState.CLOSED
            and circuit.failure_count >= circuit.failure_threshold
        ):
            circuit.state = CircuitState.OPEN
            circuit.last_state_change = datetime.utcnow()
            self._logger.warning(f"Circuit breaker OPEN: {name}")

        elif circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            circuit.last_state_change = datetime.utcnow()
            self._logger.warning(f"Circuit breaker re-OPENED: {name}")

    def _record_circuit_success(self, name: str) -> None:
        """Record circuit breaker success"""
        circuit = self._circuit_breakers.get(name)
        if not circuit:
            return

        circuit.success_count += 1

        if (
            circuit.state == CircuitState.HALF_OPEN
            and circuit.success_count >= circuit.success_threshold
        ):
            circuit.state = CircuitState.CLOSED
            circuit.failure_count = 0
            circuit.success_count = 0
            circuit.last_state_change = datetime.utcnow()
            self._logger.info(f"Circuit breaker CLOSED: {name}")

    async def execute_with_circuit_breaker(
        self,
        circuit_name: str,
        func: Callable[..., Awaitable[Any]],
        *args,
        **kwargs,
    ) -> Any:
        """Execute function with circuit breaker"""
        circuit = self._circuit_breakers.get(circuit_name)
        if not circuit:
            return await func(*args, **kwargs)

        # Check if circuit is open
        if circuit.state == CircuitState.OPEN:
            # Check if timeout has passed
            time_since_open = (datetime.utcnow() - circuit.last_state_change).seconds
            if time_since_open >= circuit.timeout:
                circuit.state = CircuitState.HALF_OPEN
                circuit.success_count = 0
                circuit.last_state_change = datetime.utcnow()
            else:
                raise Exception(f"Circuit breaker OPEN: {circuit_name}")

        try:
            result = await func(*args, **kwargs)
            self._record_circuit_success(circuit_name)
            return result
        except Exception as e:
            self._record_circuit_failure(circuit_name)
            raise

    def is_circuit_open(self, circuit_name: str) -> bool:
        """Check if circuit is open"""
        circuit = self._circuit_breakers.get(circuit_name)
        if not circuit:
            return False

        if circuit.state == CircuitState.OPEN:
            time_since_open = (datetime.utcnow() - circuit.last_state_change).seconds
            if time_since_open >= circuit.timeout:
                # Auto transition to half-open
                circuit.state = CircuitState.HALF_OPEN
                circuit.last_state_change = datetime.utcnow()
                return False
            return True

        return False

    # ============== Fallback ==============

    def register_fallback(
        self,
        operation: str,
        fallback_func: Callable,
    ) -> None:
        """Register a fallback handler"""
        self._fallback_handlers[operation] = fallback_func

    async def execute_with_fallback(
        self,
        operation: str,
        primary_func: Callable[..., Awaitable[Any]],
        fallback_func: Optional[Callable] = None,
        *args,
        **kwargs,
    ) -> Any:
        """Execute with fallback"""
        fallback = fallback_func or self._fallback_handlers.get(operation)

        try:
            return await primary_func(*args, **kwargs)
        except Exception as e:
            if fallback:
                return fallback(*args, **kwargs)
            raise

    # ============== Self-Healing ==============

    def create_self_healing_rule(
        self,
        name: str,
        error_pattern: str,
        actions: List[Dict[str, Any]],
        error_category: Optional[ErrorCategory] = None,
        severity_threshold: ErrorSeverity = ErrorSeverity.MEDIUM,
        cooldown: int = 300,
    ) -> SelfHealingRule:
        """Create a self-healing rule"""
        import re

        re.compile(error_pattern)  # Validate pattern

        rule = SelfHealingRule(
            name=name,
            error_pattern=error_pattern,
            error_category=error_category,
            severity_threshold=severity_threshold,
            actions=actions,
            cooldown=cooldown,
        )

        self._self_healing_rules[rule.id] = rule
        return rule

    def get_self_healing_rules(self) -> List[SelfHealingRule]:
        """Get self-healing rules"""
        return list(self._self_healing_rules.values())

    def enable_rule(self, rule_id: str) -> bool:
        """Enable a self-healing rule"""
        rule = self._self_healing_rules.get(rule_id)
        if not rule:
            return False
        rule.enabled = True
        return True

    def disable_rule(self, rule_id: str) -> bool:
        """Disable a self-healing rule"""
        rule = self._self_healing_rules.get(rule_id)
        if not rule:
            return False
        rule.enabled = False
        return True

    async def _check_self_healing(self, error: ErrorRecord) -> None:
        """Check if error triggers self-healing"""
        import re

        for rule in self._self_healing_rules.values():
            if not rule.enabled:
                continue

            # Check cooldown
            if rule.last_executed:
                time_since_exec = (datetime.utcnow() - rule.last_executed).seconds
                if time_since_exec < rule.cooldown:
                    continue

            # Check severity
            severity_order = [
                ErrorSeverity.LOW,
                ErrorSeverity.MEDIUM,
                ErrorSeverity.HIGH,
                ErrorSeverity.CRITICAL,
            ]
            if severity_order.index(error.severity) < severity_order.index(rule.severity_threshold):
                continue

            # Check category
            if rule.error_category and error.category != rule.error_category:
                continue

            # Check pattern
            try:
                pattern = re.compile(rule.error_pattern)
                if not pattern.search(error.message):
                    continue
            except Exception:
                continue

            # Execute self-healing actions
            await self._execute_self_healing_actions(rule, error)
            break

    async def _execute_self_healing_actions(
        self,
        rule: SelfHealingRule,
        error: ErrorRecord,
    ) -> None:
        """Execute self-healing actions"""
        rule.last_executed = datetime.utcnow()
        rule.execution_count += 1

        for action in rule.actions:
            action_type = action.get("type", "")
            action_data = action.get("data", {})

            try:
                if action_type == "retry":
                    await asyncio.sleep(action_data.get("delay", 1))
                elif action_type == "restart_service":
                    # Would restart service
                    pass
                elif action_type == "clear_cache":
                    # Would clear cache
                    pass
                elif action_type == "reset_connection":
                    # Would reset connection
                    pass
                elif action_type == "custom":
                    handler = action_data.get("handler")
                    if handler:
                        await handler(error)

                rule.success_count += 1

            except Exception as e:
                self._logger.error(f"Self-healing action failed: {e}")

    # ============== Error Handlers ==============

    def register_error_handler(
        self,
        category: ErrorCategory,
        handler: Callable[[ErrorRecord], None],
    ) -> None:
        """Register an error handler"""
        self._error_handlers[category] = handler

    # ============== Analytics ==============

    def get_error_statistics(
        self,
        service: Optional[str] = None,
        time_range: Optional[timedelta] = None,
    ) -> Dict[str, Any]:
        """Get error statistics"""
        errors = list(self._errors.values())

        if service:
            errors = [e for e in errors if e.service == service]

        if time_range:
            cutoff = datetime.utcnow() - time_range
            errors = [e for e in errors if e.timestamp >= cutoff]

        total = len(errors)
        resolved = len([e for e in errors if e.resolved])

        # Count by category
        by_category = defaultdict(int)
        by_severity = defaultdict(int)
        by_service = defaultdict(int)

        for error in errors:
            by_category[error.category.value] += 1
            by_severity[error.severity.value] += 1
            by_service[error.service] += 1

        return {
            "total": total,
            "resolved": resolved,
            "unresolved": total - resolved,
            "resolutionRate": resolved / total if total > 0 else 0,
            "byCategory": dict(by_category),
            "bySeverity": dict(by_severity),
            "byService": dict(by_service),
        }


# Singleton
_error_recovery_service: Optional[ErrorRecoveryService] = None


def get_error_recovery_service() -> ErrorRecoveryService:
    """Get the error recovery service instance"""
    global _error_recovery_service
    if _error_recovery_service is None:
        _error_recovery_service = ErrorRecoveryService()
    return _error_recovery_service
