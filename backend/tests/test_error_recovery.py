"""Tests for ErrorRecoveryService"""

import pytest
from jartbrowser.services.error_recovery import (
    ErrorRecoveryService,
    ErrorCategory,
    ErrorSeverity,
    CircuitState,
)


@pytest.fixture
def error_service():
    return ErrorRecoveryService()


def test_record_error(error_service):
    """Test error recording"""
    error = ValueError("Test error")
    record = error_service.record_error(
        error=error,
        service="test_service",
        operation="test_op",
        category=ErrorCategory.INTERNAL,
        severity=ErrorSeverity.MEDIUM,
    )
    assert record is not None
    assert record.message == "Test error"
    assert record.category == ErrorCategory.INTERNAL


def test_get_error(error_service):
    """Test getting error by ID"""
    error = error_service.record_error(
        error=ValueError("Get test"),
        service="test",
        operation="test",
    )
    retrieved = error_service.get_error(error.id)
    assert retrieved is not None
    assert retrieved.id == error.id


def test_get_errors_list(error_service):
    """Test listing errors"""
    error_service.record_error(error=ValueError("Error 1"), service="svc1", operation="op1")
    error_service.record_error(error=ValueError("Error 2"), service="svc1", operation="op2")

    errors = error_service.get_errors(service="svc1")
    assert len(errors) >= 2


def test_get_errors_by_category(error_service):
    """Test filtering by category"""
    error_service.record_error(
        error=ValueError("Network error"),
        service="test",
        operation="test",
        category=ErrorCategory.NETWORK,
    )
    errors = error_service.get_errors(category=ErrorCategory.NETWORK)
    assert any(e.category == ErrorCategory.NETWORK for e in errors)


def test_get_errors_by_severity(error_service):
    """Test filtering by severity"""
    error_service.record_error(
        error=ValueError("Critical"),
        service="test",
        operation="test",
        severity=ErrorSeverity.CRITICAL,
    )
    errors = error_service.get_errors(severity=ErrorSeverity.CRITICAL)
    assert any(e.severity == ErrorSeverity.CRITICAL for e in errors)


def test_resolve_error(error_service):
    """Test resolving error"""
    record = error_service.record_error(
        error=ValueError("To resolve"),
        service="test",
        operation="test",
    )
    result = error_service.resolve_error(record.id, "Fixed it")
    assert result is True
    resolved = error_service.get_error(record.id)
    assert resolved.resolved is True
    assert resolved.resolution == "Fixed it"


def test_create_circuit_breaker(error_service):
    """Test circuit breaker creation"""
    cb = error_service.create_circuit_breaker(
        name="test_circuit",
        failure_threshold=3,
        timeout=60,
    )
    assert cb is not None
    assert cb.name == "test_circuit"
    assert cb.state == CircuitState.CLOSED


def test_get_circuit_breaker(error_service):
    """Test getting circuit breaker"""
    error_service.create_circuit_breaker(name="get_cb")
    cb = error_service.get_circuit_breaker("get_cb")
    assert cb is not None
    assert cb.name == "get_cb"


def test_get_circuit_breakers_list(error_service):
    """Test listing circuit breakers"""
    error_service.create_circuit_breaker(name="cb1")
    error_service.create_circuit_breaker(name="cb2")
    cbs = error_service.get_circuit_breakers()
    assert len(cbs) >= 2


def test_is_circuit_open_initial_closed(error_service):
    """Test circuit starts closed"""
    error_service.create_circuit_breaker(name="closed_cb")
    assert error_service.is_circuit_open("closed_cb") is False


def test_error_statistics(error_service):
    """Test error statistics"""
    error_service.record_error(
        error=ValueError("Stat 1"),
        service="statsvc",
        operation="test",
    )
    error_service.record_error(
        error=ValueError("Stat 2"),
        service="statsvc",
        operation="test",
    )

    stats = error_service.get_error_statistics(service="statsvc")
    assert stats["total"] >= 2
    assert "byCategory" in stats
    assert "bySeverity" in stats


def test_configure_retry(error_service):
    """Test retry configuration"""
    error_service.configure_retry(
        operation="retry_test",
        max_attempts=5,
        initial_delay=0.1,
    )
    config = error_service._retry_configs["retry_test"]
    assert config["max_attempts"] == 5
    assert config["initial_delay"] == 0.1


def test_register_fallback(error_service):
    """Test fallback registration"""

    def fallback(*args):
        return "fallback_result"

    error_service.register_fallback("fallback_op", fallback)
    assert "fallback_op" in error_service._fallback_handlers
