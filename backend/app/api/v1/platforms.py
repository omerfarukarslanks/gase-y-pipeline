import secrets
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.exceptions import BadRequestException, NotFoundException
from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.platform_account import PlatformAccount
from app.models.user import User
from app.schemas.platform import PlatformAccountResponse

router = APIRouter(prefix="/platforms", tags=["platforms"])

# In-memory state store for OAuth (use Redis in production)
_oauth_states: dict[str, dict] = {}


def _get_oauth_config(platform: str) -> dict:
    """Get OAuth configuration for a given platform."""
    configs = {
        "youtube": {
            "auth_url": "https://accounts.google.com/o/oauth2/auth",
            "token_url": "https://oauth2.googleapis.com/token",
            "client_id": settings.YOUTUBE_CLIENT_ID,
            "client_secret": settings.YOUTUBE_CLIENT_SECRET,
            "redirect_uri": f"http://localhost:8000/api/v1/platforms/youtube/callback",
            "scopes": "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly",
        },
        "instagram": {
            "auth_url": "https://api.instagram.com/oauth/authorize",
            "token_url": "https://api.instagram.com/oauth/access_token",
            "client_id": settings.INSTAGRAM_APP_ID,
            "client_secret": settings.INSTAGRAM_APP_SECRET,
            "redirect_uri": f"http://localhost:8000/api/v1/platforms/instagram/callback",
            "scopes": "instagram_basic,instagram_content_publish",
        },
        "twitter": {
            "auth_url": "https://twitter.com/i/oauth2/authorize",
            "token_url": "https://api.twitter.com/2/oauth2/token",
            "client_id": settings.TWITTER_CLIENT_ID,
            "client_secret": settings.TWITTER_CLIENT_SECRET,
            "redirect_uri": f"http://localhost:8000/api/v1/platforms/twitter/callback",
            "scopes": "tweet.read tweet.write users.read offline.access",
        },
        "reddit": {
            "auth_url": "https://www.reddit.com/api/v1/authorize",
            "token_url": "https://www.reddit.com/api/v1/access_token",
            "client_id": settings.REDDIT_CLIENT_ID,
            "client_secret": settings.REDDIT_CLIENT_SECRET,
            "redirect_uri": f"http://localhost:8000/api/v1/platforms/reddit/callback",
            "scopes": "submit read identity",
        },
        "tiktok": {
            "auth_url": "https://www.tiktok.com/v2/auth/authorize/",
            "token_url": "https://open.tiktokapis.com/v2/oauth/token/",
            "client_id": settings.TIKTOK_CLIENT_KEY,
            "client_secret": settings.TIKTOK_CLIENT_SECRET,
            "redirect_uri": f"http://localhost:8000/api/v1/platforms/tiktok/callback",
            "scopes": "user.info.basic,video.publish",
        },
    }
    if platform not in configs:
        raise BadRequestException(f"Unsupported platform: {platform}")
    return configs[platform]


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
    """Generate OAuth authorization URL for a platform."""
    config = _get_oauth_config(platform)

    # Generate state parameter for CSRF protection
    state = secrets.token_urlsafe(32)
    _oauth_states[state] = {
        "user_id": str(current_user.id),
        "platform": platform,
    }

    # Build authorization URL
    params = {
        "client_id": config["client_id"],
        "redirect_uri": config["redirect_uri"],
        "response_type": "code",
        "scope": config["scopes"],
        "state": state,
    }

    # Platform-specific params
    if platform == "youtube":
        params["access_type"] = "offline"
        params["include_granted_scopes"] = "true"
    elif platform == "reddit":
        params["duration"] = "permanent"

    query_string = "&".join(f"{k}={v}" for k, v in params.items())
    oauth_url = f"{config['auth_url']}?{query_string}"

    return {"platform": platform, "oauth_url": oauth_url}


@router.get("/{platform}/callback")
async def oauth_callback(
    platform: str,
    code: str,
    state: str | None = None,
    error: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Handle OAuth callback from platform. Exchange code for tokens."""
    if error:
        return RedirectResponse(
            url=f"http://localhost:3000/accounts?error={error}&platform={platform}"
        )

    # Validate state
    if not state or state not in _oauth_states:
        raise BadRequestException("Invalid or expired OAuth state")

    state_data = _oauth_states.pop(state)
    if state_data["platform"] != platform:
        raise BadRequestException("Platform mismatch in OAuth state")

    user_id = uuid.UUID(state_data["user_id"])
    config = _get_oauth_config(platform)

    # Exchange code for tokens
    import httpx
    async with httpx.AsyncClient() as client:
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": config["redirect_uri"],
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
        }

        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Reddit uses basic auth for token exchange
        auth = None
        if platform == "reddit":
            auth = (config["client_id"], config["client_secret"])
            headers["User-Agent"] = "gase-y-pipeline/0.1"
            del token_data["client_id"]
            del token_data["client_secret"]

        # TikTok uses JSON
        if platform == "tiktok":
            token_data["client_key"] = token_data.pop("client_id")
            headers = {"Content-Type": "application/json"}
            response = await client.post(
                config["token_url"], json=token_data, headers=headers
            )
        else:
            response = await client.post(
                config["token_url"], data=token_data, headers=headers, auth=auth
            )

        if response.status_code != 200:
            return RedirectResponse(
                url=f"http://localhost:3000/accounts?error=token_exchange_failed&platform={platform}"
            )

        tokens = response.json()

    # Extract tokens (varies by platform)
    if platform == "tiktok":
        tokens = tokens.get("data", tokens)

    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    token_expires_at = None
    if expires_in:
        from datetime import timedelta
        token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=int(expires_in))

    # Get user info from platform (display name)
    display_name = None
    platform_user_id = None

    try:
        async with httpx.AsyncClient() as client:
            if platform == "youtube":
                resp = await client.get(
                    "https://www.googleapis.com/youtube/v3/channels",
                    params={"part": "snippet", "mine": "true"},
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if resp.status_code == 200:
                    items = resp.json().get("items", [])
                    if items:
                        platform_user_id = items[0]["id"]
                        display_name = items[0]["snippet"]["title"]

            elif platform == "twitter":
                resp = await client.get(
                    "https://api.twitter.com/2/users/me",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                if resp.status_code == 200:
                    user_data = resp.json().get("data", {})
                    platform_user_id = user_data.get("id")
                    display_name = user_data.get("username")

            elif platform == "reddit":
                resp = await client.get(
                    "https://oauth.reddit.com/api/v1/me",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "User-Agent": "gase-y-pipeline/0.1",
                    },
                )
                if resp.status_code == 200:
                    platform_user_id = resp.json().get("id")
                    display_name = resp.json().get("name")

            elif platform == "instagram":
                platform_user_id = str(tokens.get("user_id", ""))
                display_name = f"Instagram User {platform_user_id}"

            elif platform == "tiktok":
                platform_user_id = tokens.get("open_id", "")
                display_name = f"TikTok User"
    except Exception:
        pass  # Non-critical, continue without display name

    # Create or update platform account
    result = await db.execute(
        select(PlatformAccount).where(
            PlatformAccount.user_id == user_id,
            PlatformAccount.platform == platform,
            PlatformAccount.platform_user_id == (platform_user_id or ""),
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.access_token = access_token
        existing.refresh_token = refresh_token
        existing.token_expires_at = token_expires_at
        existing.display_name = display_name
        existing.is_active = True
    else:
        account = PlatformAccount(
            user_id=user_id,
            platform=platform,
            platform_user_id=platform_user_id or "",
            display_name=display_name,
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires_at=token_expires_at,
            is_active=True,
        )
        db.add(account)

    await db.commit()

    # Redirect back to frontend
    return RedirectResponse(
        url=f"http://localhost:3000/accounts?success=true&platform={platform}"
    )


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
