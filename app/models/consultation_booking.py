from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ConsultationBooking(TimestampMixin, Base):
    __tablename__ = "consultation_bookings"

    id: Mapped[int] = mapped_column(primary_key=True)
    contact_lead_id: Mapped[int | None] = mapped_column(
        ForeignKey("contact_leads.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    consultation_type: Mapped[str] = mapped_column(String(100), nullable=False, default="strategy")
    preferred_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str] = mapped_column(String(100), nullable=False, default="Asia/Calcutta")
    project_details: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending", index=True)
    meeting_link: Mapped[str | None] = mapped_column(String(500), nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    contact_lead: Mapped["ContactLead | None"] = relationship(back_populates="consultation_bookings")
    assigned_admin: Mapped["AdminUser | None"] = relationship(
        back_populates="managed_bookings",
        foreign_keys=[assigned_admin_id],
    )
