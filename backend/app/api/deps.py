# Re-export common dependencies for route-level use
from app.db.session import get_db
from app.dependencies import get_current_user

__all__ = ["get_db", "get_current_user"]
