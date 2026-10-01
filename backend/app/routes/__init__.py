"""
API route controllers package.
"""

from backend.app.routes.auth import router as auth_router
from backend.app.routes.health import router as health_router
from backend.app.routes.documents import router as documents_router

__all__ = ["auth_router", "health_router", "documents_router"]
