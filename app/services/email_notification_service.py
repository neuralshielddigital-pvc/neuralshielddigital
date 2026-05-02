from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.core.config import get_settings
from app.core.logging import get_logger
from app.models.consultation_booking import ConsultationBooking
from app.models.contact_lead import ContactLead


logger = get_logger("app.email")


class EmailNotificationService:
    def __init__(self):
        self.settings = get_settings()

    def _build_message(self, *, to_email: str, subject: str, body: str, reply_to: str | None = None) -> EmailMessage:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
        message["To"] = to_email
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content(body)
        return message

    def send_email(self, *, to_email: str, subject: str, body: str, reply_to: str | None = None) -> bool:
        if not self.settings.smtp_username or not self.settings.smtp_password:
            logger.warning(
                "SMTP credentials missing; skipping email send.",
                extra={"detail": f"to={to_email}, subject={subject}"},
            )
            return False

        message = self._build_message(
            to_email=to_email,
            subject=subject,
            body=body,
            reply_to=reply_to,
        )

        try:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port, timeout=30) as smtp:
                if self.settings.smtp_use_tls:
                    smtp.starttls()
                smtp.login(self.settings.smtp_username, self.settings.smtp_password)
                smtp.send_message(message)
            logger.info("Email sent successfully", extra={"detail": f"to={to_email}, subject={subject}"})
            return True
        except Exception:
            logger.exception("Failed to send email", extra={"detail": f"to={to_email}, subject={subject}"})
            return False

    def send_contact_lead_notifications(self, lead: ContactLead) -> None:
        internal_subject = f"New contact lead from {lead.full_name}"
        internal_body = (
            f"Name: {lead.full_name}\n"
            f"Email: {lead.email}\n"
            f"Phone: {lead.phone or '-'}\n"
            f"Company: {lead.company_name or '-'}\n"
            f"Service Interest: {lead.service_interest or '-'}\n"
            f"Subject: {lead.subject or '-'}\n"
            f"Source Page: {lead.source_page}\n\n"
            f"Message:\n{lead.message}\n"
        )
        self.send_email(
            to_email=self.settings.business_email,
            subject=internal_subject,
            body=internal_body,
            reply_to=lead.email,
        )

        acknowledgment_subject = "We received your inquiry"
        acknowledgment_body = (
            f"Hello {lead.full_name},\n\n"
            "Thank you for contacting NeuralShield Digital. "
            "Our team has received your inquiry and will get back to you soon.\n\n"
            "Regards,\nNeuralShield Digital"
        )
        self.send_email(
            to_email=lead.email,
            subject=acknowledgment_subject,
            body=acknowledgment_body,
        )

    def send_booking_notifications(self, booking: ConsultationBooking) -> None:
        internal_subject = f"New consultation booking from {booking.full_name}"
        internal_body = (
            f"Name: {booking.full_name}\n"
            f"Email: {booking.email}\n"
            f"Phone: {booking.phone or '-'}\n"
            f"Company: {booking.company_name or '-'}\n"
            f"Consultation Type: {booking.consultation_type}\n"
            f"Preferred DateTime: {booking.preferred_datetime or '-'}\n"
            f"Timezone: {booking.timezone}\n\n"
            f"Project Details:\n{booking.project_details}\n"
        )
        self.send_email(
            to_email=self.settings.business_email,
            subject=internal_subject,
            body=internal_body,
            reply_to=booking.email,
        )

        acknowledgment_subject = "Your consultation request has been received"
        acknowledgment_body = (
            f"Hello {booking.full_name},\n\n"
            "Thank you for booking a consultation with NeuralShield Digital. "
            "We will review your request and contact you shortly.\n\n"
            "Regards,\nNeuralShield Digital"
        )
        self.send_email(
            to_email=booking.email,
            subject=acknowledgment_subject,
            body=acknowledgment_body,
        )
