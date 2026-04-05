"""
Rate Limiter for API endpoints.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any


class RateLimiter:
    """Rate limiter for API endpoints."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = None

    async def is_allowed(self, client_id: str) -> bool:
        """
        Check if client is allowed to make request.

        Args:
            client_id: Client identifier

        Returns:
            True if allowed, False if rate limit exceeded
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            current_time = time.time()
            
            self._requests[client_id] = [
                req_time
                for req_time in self._requests[client_id]
                if current_time - req_time < self.window_seconds
            ]
            
            if len(self._requests[client_id]) >= self.max_requests:
                return False
            
            self._requests[client_id].append(current_time)
            return True

    async def get_remaining(self, client_id: str) -> int:
        """
        Get remaining requests for client.

        Args:
            client_id: Client identifier

        Returns:
            Number of remaining requests
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            current_time = time.time()
            
            self._requests[client_id] = [
                req_time
                for req_time in self._requests[client_id]
                if current_time - req_time < self.window_seconds
            ]
            
            return max(0, self.max_requests - len(self._requests[client_id]))

    async def get_reset_time(self, client_id: str) -> float:
        """
        Get time until rate limit resets.

        Args:
            client_id: Client identifier

        Returns:
            Seconds until reset
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            if not self._requests[client_id]:
                return 0.0
            
            oldest_request = min(self._requests[client_id])
            reset_time = oldest_request + self.window_seconds - time.time()
            
            return max(0.0, reset_time)

    def get_stats(self, client_id: str) -> dict[str, Any]:
        """
        Get rate limit stats for client.

        Args:
            client_id: Client identifier

        Returns:
            Rate limit statistics
        """
        current_time = time.time()
        
        self._requests[client_id] = [
            req_time
            for req_time in self._requests[client_id]
            if current_time - req_time < self.window_seconds
        ]
        
        return {
            "client_id": client_id,
            "requests_made": len(self._requests[client_id]),
            "requests_remaining": max(0, self.max_requests - len(self._requests[client_id])),
            "max_requests": self.max_requests,
            "window_seconds": self.window_seconds,
        }


class SSERateLimiter:
    """Rate limiter specifically for SSE connections."""

    def __init__(self, max_connections_per_ip: int = 5):
        self.max_connections_per_ip = max_connections_per_ip
        self._connections: dict[str, int] = defaultdict(int)
        self._lock = None

    async def can_connect(self, ip_address: str) -> bool:
        """
        Check if IP can open new SSE connection.

        Args:
            ip_address: Client IP address

        Returns:
            True if allowed, False if limit reached
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            return self._connections[ip_address] < self.max_connections_per_ip

    async def add_connection(self, ip_address: str) -> None:
        """
        Register a new SSE connection.

        Args:
            ip_address: Client IP address
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            self._connections[ip_address] += 1

    async def remove_connection(self, ip_address: str) -> None:
        """
        Remove an SSE connection.

        Args:
            ip_address: Client IP address
        """
        import asyncio
        
        if self._lock is None:
            self._lock = asyncio.Lock()
        
        async with self._lock:
            if self._connections[ip_address] > 0:
                self._connections[ip_address] -= 1

    def get_connection_count(self, ip_address: str) -> int:
        """
        Get connection count for IP.

        Args:
            ip_address: Client IP address

        Returns:
            Number of active connections
        """
        return self._connections[ip_address]
