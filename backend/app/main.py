import asyncio
import json
import logging

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1.router import api_v1_router

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for real-time job status updates."""

    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected: user={user_id}")

    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id] = [
                ws for ws in self.active_connections[user_id] if ws != websocket
            ]
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected: user={user_id}")

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            dead = []
            for ws in self.active_connections[user_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.active_connections[user_id].remove(ws)

    async def broadcast(self, message: dict):
        for user_id in self.active_connections:
            await self.send_to_user(user_id, message)


manager = ConnectionManager()


def create_app() -> FastAPI:
    application = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_v1_router, prefix="/api/v1")

    # Store manager on app state for access from other modules
    application.state.ws_manager = manager

    @application.on_event("startup")
    async def startup_redis_listener():
        """Start background task to listen for Redis pub/sub notifications."""
        async def redis_listener():
            import redis.asyncio as aioredis
            r = aioredis.from_url(settings.REDIS_URL)
            pubsub = r.pubsub()
            await pubsub.subscribe("gasey:job_updates")
            try:
                async for message in pubsub.listen():
                    if message["type"] == "message":
                        try:
                            data = json.loads(message["data"])
                            user_id = data.pop("user_id", None)
                            if user_id:
                                await manager.send_to_user(user_id, data)
                        except (json.JSONDecodeError, Exception) as e:
                            logger.warning(f"Failed to process Redis message: {e}")
            except asyncio.CancelledError:
                await pubsub.unsubscribe("gasey:job_updates")
                await r.close()

        application.state.redis_listener_task = asyncio.create_task(redis_listener())

    @application.on_event("shutdown")
    async def shutdown_redis_listener():
        task = getattr(application.state, "redis_listener_task", None)
        if task:
            task.cancel()

    @application.get("/api/health")
    async def health_check():
        return {"status": "healthy", "service": settings.APP_NAME}

    @application.websocket("/ws/jobs/{user_id}")
    async def websocket_jobs(websocket: WebSocket, user_id: str):
        """
        WebSocket endpoint for real-time job status updates.

        Clients connect with their user_id and receive updates about:
        - Video generation progress (step changes, completion, failure)
        - Publish job status changes
        - Scheduled job dispatches
        """
        await manager.connect(websocket, user_id)
        try:
            while True:
                # Keep connection alive. Clients can also send messages.
                data = await websocket.receive_text()
                # Handle ping/pong or client commands
                if data == "ping":
                    await websocket.send_text("pong")
                else:
                    # Echo back or handle client requests
                    try:
                        msg = json.loads(data)
                        if msg.get("type") == "subscribe_job":
                            # Client subscribes to a specific job
                            await websocket.send_json({
                                "type": "subscribed",
                                "job_id": msg.get("job_id"),
                            })
                    except json.JSONDecodeError:
                        pass
        except WebSocketDisconnect:
            manager.disconnect(websocket, user_id)
        except Exception:
            manager.disconnect(websocket, user_id)

    return application


app = create_app()
