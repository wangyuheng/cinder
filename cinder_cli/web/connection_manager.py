"""
SSE Connection Manager - Manages multiple SSE connections.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any
from weakref import WeakSet

from fastapi import WebSocket


class SSEConnectionManager:
    """Manages SSE connections with limits and timeouts."""

    def __init__(self, max_connections: int = 10, timeout: int = 1800):
        self.max_connections = max_connections
        self.timeout = timeout
        self._connections: WeakSet[Any] = WeakSet()
        self._connection_times: dict[int, float] = {}
        self._lock = asyncio.Lock()

    async def add_connection(self, connection: Any) -> bool:
        """
        Add a new connection.

        Args:
            connection: Connection to add

        Returns:
            True if connection added, False if limit reached
        """
        async with self._lock:
            if len(self._connections) >= self.max_connections:
                return False
            
            self._connections.add(connection)
            self._connection_times[id(connection)] = time.time()
            return True

    async def remove_connection(self, connection: Any) -> None:
        """
        Remove a connection.

        Args:
            connection: Connection to remove
        """
        async with self._lock:
            self._connections.discard(connection)
            self._connection_times.pop(id(connection), None)

    async def is_connection_expired(self, connection: Any) -> bool:
        """
        Check if connection has expired.

        Args:
            connection: Connection to check

        Returns:
            True if expired, False otherwise
        """
        async with self._lock:
            conn_time = self._connection_times.get(id(connection), 0)
            return time.time() - conn_time > self.timeout

    async def cleanup_expired(self) -> int:
        """
        Remove expired connections.

        Returns:
            Number of connections removed
        """
        async with self._lock:
            expired = []
            current_time = time.time()
            
            for conn_id, conn_time in self._connection_times.items():
                if current_time - conn_time > self.timeout:
                    expired.append(conn_id)
            
            for conn_id in expired:
                self._connection_times.pop(conn_id, None)
            
            return len(expired)

    def get_connection_count(self) -> int:
        """
        Get current connection count.

        Returns:
            Number of active connections
        """
        return len(self._connections)

    def get_connection_stats(self) -> dict[str, Any]:
        """
        Get connection statistics.

        Returns:
            Connection statistics
        """
        current_time = time.time()
        
        return {
            "active_connections": len(self._connections),
            "max_connections": self.max_connections,
            "timeout_seconds": self.timeout,
            "oldest_connection_age": max(
                [current_time - t for t in self._connection_times.values()] or [0]
            ),
        }


class WebSocketManager:
    """Manages WebSocket connections for progress updates."""

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self._connections: dict[int, WebSocket] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, client_id: int) -> bool:
        """
        Accept a new WebSocket connection.

        Args:
            websocket: WebSocket connection
            client_id: Client identifier

        Returns:
            True if connection accepted, False if limit reached
        """
        async with self._lock:
            if len(self._connections) >= self.max_connections:
                await websocket.close(code=1013, reason="Connection limit reached")
                return False
            
            await websocket.accept()
            self._connections[client_id] = websocket
            return True

    async def disconnect(self, client_id: int) -> None:
        """
        Disconnect a client.

        Args:
            client_id: Client identifier
        """
        async with self._lock:
            if client_id in self._connections:
                del self._connections[client_id]

    async def broadcast(self, message: dict[str, Any]) -> None:
        """
        Broadcast message to all connections.

        Args:
            message: Message to broadcast
        """
        async with self._lock:
            disconnected = []
            
            for client_id, websocket in self._connections.items():
                try:
                    await websocket.send_json(message)
                except Exception:
                    disconnected.append(client_id)
            
            for client_id in disconnected:
                del self._connections[client_id]

    async def send_to_client(self, client_id: int, message: dict[str, Any]) -> bool:
        """
        Send message to specific client.

        Args:
            client_id: Client identifier
            message: Message to send

        Returns:
            True if sent, False if client not found
        """
        async with self._lock:
            if client_id not in self._connections:
                return False
            
            try:
                await self._connections[client_id].send_json(message)
                return True
            except Exception:
                del self._connections[client_id]
                return False

    def get_connection_count(self) -> int:
        """
        Get current connection count.

        Returns:
            Number of active connections
        """
        return len(self._connections)
