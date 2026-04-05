"""
Tests for connection manager and rate limiter.
"""

from __future__ import annotations

import asyncio

import pytest

from cinder_cli.web.connection_manager import SSEConnectionManager, WebSocketManager
from cinder_cli.web.rate_limiter import RateLimiter, SSERateLimiter


@pytest.mark.asyncio
async def test_sse_connection_manager_add():
    """Test adding connections to SSE manager."""
    manager = SSEConnectionManager(max_connections=2)
    
    conn1 = Mock()
    conn2 = Mock()
    
    assert await manager.add_connection(conn1) is True
    assert await manager.add_connection(conn2) is True
    assert manager.get_connection_count() == 2


@pytest.mark.asyncio
async def test_sse_connection_manager_limit():
    """Test connection limit enforcement."""
    manager = SSEConnectionManager(max_connections=2)
    
    conn1 = Mock()
    conn2 = Mock()
    conn3 = Mock()
    
    await manager.add_connection(conn1)
    await manager.add_connection(conn2)
    
    assert await manager.add_connection(conn3) is False


@pytest.mark.asyncio
async def test_sse_connection_manager_remove():
    """Test removing connections."""
    manager = SSEConnectionManager(max_connections=2)
    
    conn = Mock()
    await manager.add_connection(conn)
    assert manager.get_connection_count() == 1
    
    await manager.remove_connection(conn)
    assert manager.get_connection_count() == 0


@pytest.mark.asyncio
async def test_sse_connection_manager_expiry():
    """Test connection expiry."""
    manager = SSEConnectionManager(max_connections=2, timeout=1)
    
    conn = Mock()
    await manager.add_connection(conn)
    
    assert await manager.is_connection_expired(conn) is False
    
    await asyncio.sleep(1.1)
    
    assert await manager.is_connection_expired(conn) is True


@pytest.mark.asyncio
async def test_rate_limiter_allowed():
    """Test rate limiter allows requests."""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    for _ in range(5):
        assert await limiter.is_allowed("client1") is True


@pytest.mark.asyncio
async def test_rate_limiter_blocked():
    """Test rate limiter blocks excess requests."""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    for _ in range(5):
        await limiter.is_allowed("client1")
    
    assert await limiter.is_allowed("client1") is False


@pytest.mark.asyncio
async def test_rate_limiter_remaining():
    """Test rate limiter remaining count."""
    limiter = RateLimiter(max_requests=5, window_seconds=60)
    
    assert await limiter.get_remaining("client1") == 5
    
    await limiter.is_allowed("client1")
    assert await limiter.get_remaining("client1") == 4


@pytest.mark.asyncio
async def test_sse_rate_limiter():
    """Test SSE rate limiter."""
    limiter = SSERateLimiter(max_connections_per_ip=3)
    
    ip = "192.168.1.1"
    
    assert await limiter.can_connect(ip) is True
    
    await limiter.add_connection(ip)
    await limiter.add_connection(ip)
    await limiter.add_connection(ip)
    
    assert await limiter.can_connect(ip) is False
    
    await limiter.remove_connection(ip)
    
    assert await limiter.can_connect(ip) is True


@pytest.mark.asyncio
async def test_websocket_manager():
    """Test WebSocket manager."""
    manager = WebSocketManager(max_connections=2)
    
    ws1 = Mock()
    ws1.accept = Mock(return_value=asyncio.coroutine(lambda: None)())
    ws1.send_json = Mock(return_value=asyncio.coroutine(lambda data: None)())
    
    ws2 = Mock()
    ws2.accept = Mock(return_value=asyncio.coroutine(lambda: None)())
    ws2.send_json = Mock(return_value=asyncio.coroutine(lambda data: None)())
    
    assert await manager.connect(ws1, 1) is True
    assert await manager.connect(ws2, 2) is True
    assert manager.get_connection_count() == 2


@pytest.mark.asyncio
async def test_websocket_manager_broadcast():
    """Test WebSocket broadcast."""
    manager = WebSocketManager(max_connections=2)
    
    ws = Mock()
    ws.accept = Mock(return_value=asyncio.coroutine(lambda: None)())
    ws.send_json = Mock(return_value=asyncio.coroutine(lambda data: None)())
    
    await manager.connect(ws, 1)
    
    message = {"test": "data"}
    await manager.broadcast(message)
    
    ws.send_json.assert_called_once_with(message)
