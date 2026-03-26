import uuid

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class VideoVariant(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "video_variants"

    video_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False
    )
    language: Mapped[str] = mapped_column(String(10), nullable=False)  # en, tr, de...
    file_url: Mapped[str | None] = mapped_column(String(512))
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger)
    tts_provider: Mapped[str | None] = mapped_column(String(50))
    tts_voice_id: Mapped[str | None] = mapped_column(String(100))
    narration_url: Mapped[str | None] = mapped_column(String(512))
    subtitle_url: Mapped[str | None] = mapped_column(String(512))
    title: Mapped[str | None] = mapped_column(String(500))
    description: Mapped[str | None] = mapped_column(Text)
    hashtags: Mapped[list | None] = mapped_column(ARRAY(String))
    status: Mapped[str] = mapped_column(String(50), default="pending")

    # Relationships
    video = relationship("Video", back_populates="variants")
    publish_jobs = relationship("PublishJob", back_populates="video_variant", cascade="all, delete-orphan")
