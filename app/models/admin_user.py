from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class AdminUser(TimestampMixin, Base):
    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="super_admin")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_login_ip: Mapped[str | None] = mapped_column(String(64), nullable=True)

    blog_posts: Mapped[list["BlogPost"]] = relationship(
        back_populates="author",
        passive_deletes=True,
    )
    assigned_contact_leads: Mapped[list["ContactLead"]] = relationship(
        back_populates="assigned_admin",
        passive_deletes=True,
        foreign_keys="ContactLead.assigned_admin_id",
    )
    managed_bookings: Mapped[list["ConsultationBooking"]] = relationship(
        back_populates="assigned_admin",
        passive_deletes=True,
        foreign_keys="ConsultationBooking.assigned_admin_id",
    )

    def mark_login(self, ip_address: str | None = None) -> None:
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
