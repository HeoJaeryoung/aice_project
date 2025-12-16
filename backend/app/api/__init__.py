from app.api.auth import router as auth_router
from app.api.questions import router as questions_router
from app.api.study import router as study_router
from app.api.dashboard import router as dashboard_router

__all__ = ["auth_router", "questions_router", "study_router", "dashboard_router"]
