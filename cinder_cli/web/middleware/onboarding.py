"""
Onboarding middleware for checking user onboarding status.
"""

from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse, Response

from cinder_cli.database.user_dao import UserDAO


class OnboardingMiddleware(BaseHTTPMiddleware):
    """Onboarding middleware for checking user onboarding status."""
    
    PUBLIC_PATHS = [
        "/onboarding",
        "/api/invitations",
        "/api/users",
        "/api/health",
        "/api/soul/questionnaire",
    ]
    
    def __init__(self, app):
        super().__init__(app)
        self.user_dao = UserDAO()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Dispatch request with onboarding check."""
        path = request.url.path
        
        if self._is_public_path(path):
            return await call_next(request)
        
        user_id = getattr(request.state, "user_id", None)
        
        if user_id is None:
            return RedirectResponse(url="/onboarding/invitation", status_code=302)
        
        user = self.user_dao.get_by_id(user_id)
        
        if user is None or not user.onboarding_completed:
            return RedirectResponse(url="/onboarding/invitation", status_code=302)
        
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """Check if path is public."""
        for public_path in self.PUBLIC_PATHS:
            if path.startswith(public_path):
                return True
        return False
