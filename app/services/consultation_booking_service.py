from __future__ import annotations

from sqlalchemy import select

from app.models.consultation_booking import ConsultationBooking
from app.models.contact_lead import ContactLead
from app.schemas.booking import ConsultationBookingCreate, ConsultationBookingUpdate
from app.services.base import BaseService, NotFoundError
from app.services.email_notification_service import EmailNotificationService


class ConsultationBookingService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.email_service = EmailNotificationService()

    def create_booking(self, payload: ConsultationBookingCreate) -> ConsultationBooking:
        contact_lead_id = payload.contact_lead_id
        if not contact_lead_id:
            lead = ContactLead(
                full_name=payload.full_name,
                email=payload.email,
                phone=payload.phone,
                company_name=payload.company_name,
                message=payload.project_details,
                service_interest=payload.consultation_type,
                source_page="/book-consultation",
                lead_source="website",
                status="new",
                priority="normal",
            )
            self.db.add(lead)
            self.db.flush()
            contact_lead_id = lead.id

        booking = ConsultationBooking(
            **payload.model_dump(exclude={"contact_lead_id"}),
            contact_lead_id=contact_lead_id,
        )
        booking = self.add_and_commit(booking)
        self.email_service.send_booking_notifications(booking)
        return booking

    def get_booking(self, booking_id: int) -> ConsultationBooking:
        booking = self.db.get(ConsultationBooking, booking_id)
        if not booking:
            raise NotFoundError("Consultation booking not found.")
        return booking

    def list_bookings(self, *, status: str | None = None, limit: int = 100) -> list[ConsultationBooking]:
        statement = select(ConsultationBooking).order_by(ConsultationBooking.created_at.desc()).limit(limit)
        if status:
            statement = statement.where(ConsultationBooking.status == status)
        return list(self.db.scalars(statement))

    def update_booking(self, booking_id: int, payload: ConsultationBookingUpdate) -> ConsultationBooking:
        booking = self.get_booking(booking_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(booking, field, value)
        self.commit()
        self.db.refresh(booking)
        return booking

    def delete_booking(self, booking_id: int) -> None:
        booking = self.get_booking(booking_id)
        self.delete_and_commit(booking)
