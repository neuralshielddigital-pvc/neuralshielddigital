from __future__ import annotations

from sqlalchemy import select

from app.models.contact_lead import ContactLead
from app.schemas.contact import ContactLeadUpdate, ContactSubmissionCreate
from app.services.base import BaseService, NotFoundError
from app.services.email_notification_service import EmailNotificationService


class ContactLeadService(BaseService):
    def __init__(self, db):
        super().__init__(db)
        self.email_service = EmailNotificationService()

    def create_lead(self, payload: ContactSubmissionCreate) -> ContactLead:
        lead = ContactLead(**payload.model_dump())
        lead = self.add_and_commit(lead)
        self.email_service.send_contact_lead_notifications(lead)
        return lead

    def get_lead(self, lead_id: int) -> ContactLead:
        lead = self.db.get(ContactLead, lead_id)
        if not lead:
            raise NotFoundError("Contact lead not found.")
        return lead

    def list_leads(self, *, status: str | None = None, limit: int = 100) -> list[ContactLead]:
        statement = select(ContactLead).order_by(ContactLead.created_at.desc()).limit(limit)
        if status:
            statement = statement.where(ContactLead.status == status)
        return list(self.db.scalars(statement))

    def update_lead(self, lead_id: int, payload: ContactLeadUpdate) -> ContactLead:
        lead = self.get_lead(lead_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)
        self.commit()
        self.db.refresh(lead)
        return lead

    def delete_lead(self, lead_id: int) -> None:
        lead = self.get_lead(lead_id)
        self.delete_and_commit(lead)
