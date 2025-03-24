"""Routes package initialization."""
from .base import app_routes
from .auth import auth_bp

__all__ = ['app_routes', 'auth_bp'] 