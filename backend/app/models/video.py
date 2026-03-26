import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class Video(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "videos"

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    script: Mapped[dict] = mapped_column(JSONB, nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(10), nullable=False, default="16:9")
    resolution: Mapped[str] = mapped_column(String(20), default="1080p")
    duration_sec: Mapped[float | None] = mapped_column(Float)
    thumbnail_url: Mapped[str | None] = mapped_column(String(512))
    watermark_url: Mapped[str | None] = mapped_column(String(512))
    bg_music_track: Mapped[str | None] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="pending")
    error_message: Mapped[str | None] = mapped_column(Text)

    # Relationships
    project = relationship("Project", back_populates="videos")
    variants = relationship("VideoVariant", back_populates="video", cascade="all, delete-orphan")
