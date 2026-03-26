import uuid

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.platform_account import PlatformAccount
from app.models.user import User
from app.schemas.platform import PlatformAccountResponse

router = APIRouter(prefix="/platforms", tags=["platforms"])


@router.get("/", response_model=list[PlatformAccountResponse])
async def list_platform_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlatformAccount).where(PlatformAccount.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/{platform}/oauth-url")
async def get_oauth_url(
    platform: str,
    current_user: User = Depends(get_current_user),
):
    # TODO: Implement OAuth URL generation per platform
    # Each platform (youtube, instagram, twitter, reddit, tiktok) has its own OAuth flow
    return {
        "platform": platform,
        "oauth_url": f"https://{platform}.com/oauth/authorize?...",
        "message": "OAuth URL generation not yet implemented",
    }


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    # TODO: Exchange code for tokens, create PlatformAccount
    return {"platform": platform, "message": "OAuth callback not yet implemented"}


@router.delete("/{account_id}")
async def disconnect_platform(
    account_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.id == account_id,
            PlatformAccount.user_id == current_user.id,
        )
    )
    account = result.scalar_one_or_none()
    if not account:
        raise NotFoundException("Platform account not found")

    await db.delete(account)
    return {"message": f"{account.platform} account disconnected"}
