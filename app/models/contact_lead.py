from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.mixins import TimestampMixin


class ContactLead(TimestampMixin, Base):
    __tablename__ = "contact_leads"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    company_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(255), nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    service_interest: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source_page: Mapped[str] = mapped_column(String(255), nullable=False, default="/contact")
    lead_source: Mapped[str] = mapped_column(String(100), nullable=False, default="website")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="new", index=True)
    priority: Mapped[str] = mapped_column(String(50), nullable=False, default="normal")
    budget_range: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_admin_id: Mapped[int | None] = mapped_column(
        ForeignKey("admin_users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    assigned_admin: Mapped["AdminUser | None"] = relationship(
        back_populates="assigned_contact_leads",
        foreign_keys=[assigned_admin_id],
    )
    consultation_bookings: Mapped[list["ConsultationBooking"]] = relationship(
        back_populates="contact_lead",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
