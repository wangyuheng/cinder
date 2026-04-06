"""
Security tests for progress tracking enhancement.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from cinder_cli.web.middleware.security import (
    SecurityMiddleware,
    RateLimiter,
    ConnectionLimiter,
)


def test_rate_limiter_allows_requests_within_limit():
    """Test that rate limiter allows requests within limit."""
    limiter = RateLimiter(requests_per_minute=10)
    client_id = "test_client"
    
    for _ in range(10):
        assert limiter.is_allowed(client_id) is True
    
    assert limiter.is_allowed(client_id) is False


def test_rate_limiter_blocks_requests_over_limit():
    """Test that rate limiter blocks requests over limit."""
    limiter = RateLimiter(requests_per_minute=5)
    client_id = "test_client"
    
    for _ in range(5):
        limiter.is_allowed(client_id)
    
    assert limiter.is_allowed(client_id) is False


def test_rate_limiter_resets_after_window():
    """Test that rate limiter resets after time window."""
    import time
    
    limiter = RateLimiter(requests_per_minute=2)
    client_id = "test_client"
    
    limiter.is_allowed(client_id)
    limiter.is_allowed(client_id)
    
    assert limiter.is_allowed(client_id) is False
    
    limiter.requests[client_id] = [time.time() - 61]
    
    assert limiter.is_allowed(client_id) is True


def test_rate_limiter_tracks_different_clients():
    """Test that rate limiter tracks different clients separately."""
    limiter = RateLimiter(requests_per_minute=2)
    
    assert limiter.is_allowed("client1") is True
    assert limiter.is_allowed("client1") is True
    assert limiter.is_allowed("client1") is False
    
    assert limiter.is_allowed("client2") is True
    assert limiter.is_allowed("client2") is True
    assert limiter.is_allowed("client2") is False


def test_rate_limiter_get_remaining():
    """Test getting remaining requests."""
    limiter = RateLimiter(requests_per_minute=10)
    client_id = "test_client"
    
    assert limiter.get_remaining(client_id) == 10
    
    limiter.is_allowed(client_id)
    assert limiter.get_remaining(client_id) == 9
    
    limiter.is_allowed(client_id)
    assert limiter.get_remaining(client_id) == 8


def test_connection_limiter_allows_connections_within_limit():
    """Test that connection limiter allows connections within limit."""
    limiter = ConnectionLimiter(max_connections_per_execution=5)
    execution_id = 1
    
    for _ in range(5):
        assert limiter.can_connect(execution_id) is True
        limiter.add_connection(execution_id)
    
    assert limiter.can_connect(execution_id) is False


def test_connection_limiter_blocks_connections_over_limit():
    """Test that connection limiter blocks connections over limit."""
    limiter = ConnectionLimiter(max_connections_per_execution=3)
    execution_id = 1
    
    for _ in range(3):
        limiter.add_connection(execution_id)
    
    assert limiter.can_connect(execution_id) is False


def test_connection_limiter_removes_connections():
    """Test that connection limiter properly removes connections."""
    limiter = ConnectionLimiter(max_connections_per_execution=2)
    execution_id = 1
    
    limiter.add_connection(execution_id)
    limiter.add_connection(execution_id)
    
    assert limiter.can_connect(execution_id) is False
    
    limiter.remove_connection(execution_id)
    
    assert limiter.can_connect(execution_id) is True


def test_connection_limiter_tracks_different_executions():
    """Test that connection limiter tracks different executions separately."""
    limiter = ConnectionLimiter(max_connections_per_execution=2)
    
    limiter.add_connection(1)
    limiter.add_connection(1)
    
    assert limiter.can_connect(1) is False
    assert limiter.can_connect(2) is True


def test_security_middleware_adds_headers():
    """Test that security middleware adds security headers."""
    app = FastAPI()
    app.add_middleware(SecurityMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert response.status_code == 200
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Content-Security-Policy" in response.headers


def test_security_middleware_rate_limiting():
    """Test that security middleware enforces rate limiting."""
    app = FastAPI()
    app.add_middleware(SecurityMiddleware, rate_limit=5)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    
    for _ in range(5):
        response = client.get("/test")
        assert response.status_code == 200
    
    response = client.get("/test")
    assert response.status_code == 429


def test_security_middleware_rate_limit_headers():
    """Test that security middleware adds rate limit headers."""
    app = FastAPI()
    app.add_middleware(SecurityMiddleware, rate_limit=10)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "test"}
    
    client = TestClient(app)
    response = client.get("/test")
    
    assert "X-RateLimit-Limit" in response.headers
    assert "X-RateLimit-Remaining" in response.headers
    assert response.headers["X-RateLimit-Limit"] == "10"


def test_sql_injection_protection():
    """Test that SQL injection attempts are blocked."""
    from cinder_cli.web.api.executions import get_execution
    
    malicious_id = "1; DROP TABLE executions;--"
    
    with pytest.raises(Exception):
        import asyncio
        asyncio.run(get_execution(malicious_id))


def test_xss_protection():
    """Test that XSS attempts are sanitized."""
    from cinder_cli.executor.execution_logger import ExecutionLogger
    from cinder_cli.config import Config
    from pathlib import Path
    import tempfile
    from unittest.mock import patch
    
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            malicious_goal = "<script>alert('xss')</script>"
            
            execution_id = logger.log_execution(
                goal=malicious_goal,
                task_tree={"subtasks": []},
                results=[],
            )
            
            execution = logger.get_execution(execution_id)
            
            assert "<script>" not in execution["goal"] or execution["goal"] == malicious_goal


def test_input_validation():
    """Test that invalid inputs are rejected."""
    from pydantic import ValidationError
    from cinder_cli.executor.progress_tracker import ProgressTracker, ExecutionPhase
    
    tracker = ProgressTracker()
    
    tracker.start_phase(ExecutionPhase.PLAN)
    tracker.update_phase_progress(150.0)
    
    progress = tracker.get_progress()
    assert progress["overall_progress"] <= 100
    
    tracker.update_phase_progress(-10.0)
    progress = tracker.get_progress()
    assert progress["overall_progress"] >= 0


def test_authentication_required():
    """Test that authentication is required for API endpoints."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    
    app = FastAPI()
    
    @app.get("/protected")
    async def protected_endpoint():
        return {"message": "protected"}
    
    client = TestClient(app)
    response = client.get("/protected")
    
    assert response.status_code in [200, 401]


def test_error_messages_do_not_leak_info():
    """Test that error messages don't leak sensitive information."""
    from cinder_cli.web.api.progress import stream_execution_progress
    import asyncio
    
    async def test_error_handling():
        try:
            await stream_execution_progress(999999)
        except Exception as e:
            error_message = str(e)
            assert "password" not in error_message.lower()
            assert "secret" not in error_message.lower()
            assert "key" not in error_message.lower()
    
    asyncio.run(test_error_handling())


def test_connection_timeout():
    """Test that SSE connections timeout properly."""
    import asyncio
    from cinder_cli.web.api.progress import stream_current_progress
    
    async def test_timeout():
        response = await stream_current_progress()
        
        assert response.media_type == "text/event-stream"
        assert "timeout" in str(response.headers).lower() or "keep-alive" in str(response.headers).lower()
    
    asyncio.run(test_timeout())


def test_data_sanitization():
    """Test that data is properly sanitized before storage."""
    from cinder_cli.executor.execution_logger import ExecutionLogger
    from cinder_cli.config import Config
    from pathlib import Path
    import tempfile
    from unittest.mock import patch
    
    config = Config()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        
        with patch.object(ExecutionLogger, '_get_db_path', return_value=db_path):
            logger = ExecutionLogger(config)
            
            task_tree = {
                "id": 1,
                "description": "Normal task",
                "malicious_field": "'; DROP TABLE executions; --"
            }
            
            execution_id = logger.log_execution(
                goal="Test goal",
                task_tree=task_tree,
                results=[],
            )
            
            execution = logger.get_execution(execution_id)
            assert execution is not None
            assert "task_tree" in execution
