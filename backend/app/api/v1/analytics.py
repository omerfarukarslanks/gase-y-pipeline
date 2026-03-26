from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview")
async def get_overview(current_user: User = Depends(get_current_user)):
    # TODO: Aggregate analytics from all publish jobs
    return {
        "total_videos": 0,
        "total_views": 0,
        "total_likes": 0,
        "total_shares": 0,
        "platforms": {},
    }
