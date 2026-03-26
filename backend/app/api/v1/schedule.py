from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/schedule", tags=["schedule"])


@router.get("/calendar")
async def get_calendar(current_user: User = Depends(get_current_user)):
    # TODO: Return scheduled publish jobs within date range
    return {"events": []}
