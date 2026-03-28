import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin


class PublishJob(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "publish_jobs"

    video_variant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("video_variants.id", ondelete="CASCADE"), nullable=False
    )
    platform_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("platform_accounts.id"), nullable=False
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    platform_post_id: Mapped[str | None] = mapped_column(String(255))
    platform_url: Mapped[str | None] = mapped_column(String(512))
    status: Mapped[str] = mapped_column(
        String(50), default="pending"
    )  # pending, scheduled, publishing, published, failed
    error_message: Mapped[str | None] = mapped_column(Text)
    publish_metadata: Mapped[dict | None] = mapped_column("metadata", JSONB, default=dict)

    # Relationships
    video_variant = relationship("VideoVariant", back_populates="publish_jobs")
    platform_account = relationship("PlatformAccount", back_populates="publish_jobs")
    analytics_snapshots = relationship("AnalyticsSnapshot", back_populates="publish_job", cascade="all, delete-orphan")
