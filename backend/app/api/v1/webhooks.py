from fastapi import APIRouter, Depends

from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/")
async def register_webhook(current_user: User = Depends(get_current_user)):
    # TODO: Register webhook URL for external integrations
    return {"message": "Webhook registration not yet implemented"}


@router.get("/")
async def list_webhooks(current_user: User = Depends(get_current_user)):
    return {"webhooks": []}
