from __future__ import annotations

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.mixins import TimestampMixin


class PageSEO(TimestampMixin, Base):
    __tablename__ = "page_seo"
    __table_args__ = (
        UniqueConstraint("page_type", "object_id", name="uq_page_seo_page_type_object_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    page_key: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    page_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    object_id: Mapped[int | None] = mapped_column(nullable=True, index=True)
    page_path: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    meta_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    meta_keywords: Mapped[str | None] = mapped_column(String(500), nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    robots: Mapped[str] = mapped_column(String(100), nullable=False, default="index,follow")
    og_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    og_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    og_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    twitter_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    twitter_description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    twitter_image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    schema_json: Mapped[str | None] = mapped_column(Text, nullable=True)
