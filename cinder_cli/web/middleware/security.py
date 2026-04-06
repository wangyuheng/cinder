"""
Security middleware for Web API.
"""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Dict, List

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimiter:
    """Rate limiter for API endpoints."""
    
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make request."""
        current_time = time.time()
        
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if current_time - t < 60
        ]
        
        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False
        
        self.requests[client_id].append(current_time)
        return True
    
    def get_remaining(self, client_id: str) -> int:
        """Get remaining requests for client."""
        current_time = time.time()
        
        self.requests[client_id] = [
            t for t in self.requests[client_id]
            if current_time - t < 60
        ]
        
        return max(0, self.requests_per_minute - len(self.requests[client_id]))


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers and rate limiting."""
    
    def __init__(self, app, rate_limit: int = 100):
        super().__init__(app)
        self.rate_limiter = RateLimiter(requests_per_minute=rate_limit)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = self._get_client_ip(request)
        
        if not self.rate_limiter.is_allowed(client_ip):
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded. Please try again later."
            )
        
        response = await call_next(request)
        
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline';"
        )
        
        response.headers["X-RateLimit-Limit"] = str(self.rate_limiter.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(
            self.rate_limiter.get_remaining(client_ip)
        )
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP address from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        return request.client.host if request.client else "unknown"


class ConnectionLimiter:
    """Limiter for SSE connections."""
    
    def __init__(self, max_connections_per_execution: int = 10):
        self.max_connections = max_connections_per_execution
        self.connections: Dict[int, int] = defaultdict(int)
    
    def can_connect(self, execution_id: int) -> bool:
        """Check if new connection is allowed for execution."""
        return self.connections[execution_id] < self.max_connections
    
    def add_connection(self, execution_id: int) -> None:
        """Register new connection."""
        self.connections[execution_id] += 1
    
    def remove_connection(self, execution_id: int) -> None:
        """Unregister connection."""
        if self.connections[execution_id] > 0:
            self.connections[execution_id] -= 1


connection_limiter = ConnectionLimiter()
