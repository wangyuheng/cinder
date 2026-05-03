"""
Session middleware for FastAPI.
"""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from cinder_cli.web.session import SessionManager


class SessionMiddleware(BaseHTTPMiddleware):
    """Session middleware for validating user sessions."""
    
    def __init__(self, app, session_cookie_name: str = "session_id"):
        super().__init__(app)
        self.session_cookie_name = session_cookie_name
        self.session_manager = SessionManager()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Dispatch request with session validation."""
        session_id = request.cookies.get(self.session_cookie_name)
        
        request.state.session_id = session_id
        request.state.user_id = None
        
        if session_id:
            user_id = self.session_manager.get_user_id(session_id)
            if user_id:
                request.state.user_id = user_id
        
        response = await call_next(request)
        
        return response
