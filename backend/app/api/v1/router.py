from fastapi import APIRouter

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.platforms import router as platforms_router
from app.api.v1.projects import router as projects_router
from app.api.v1.publish import router as publish_router
from app.api.v1.schedule import router as schedule_router
from app.api.v1.templates import router as templates_router
from app.api.v1.videos import router as videos_router
from app.api.v1.webhooks import router as webhooks_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(projects_router)
api_v1_router.include_router(videos_router)
api_v1_router.include_router(platforms_router)
api_v1_router.include_router(publish_router)
api_v1_router.include_router(templates_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(schedule_router)
api_v1_router.include_router(webhooks_router)
