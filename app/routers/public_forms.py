from __future__ import annotations

from pathlib import Path
from unittest import result

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.forms.consultation import ConsultationBookingForm
from app.forms.contact import ContactForm
from app.routers.deps import get_database
from app.schemas.booking import ConsultationBookingCreate
from app.schemas.contact import ContactSubmissionCreate
from app.services.consultation_booking_service import ConsultationBookingService
from app.services.contact_lead_service import ContactLeadService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(tags=["public-forms"])


def _meta_defaults(title: str, description: str, path: str, domain: str) -> dict:
    return {
        "page_title": title,
        "meta_description": description,
        "meta_keywords": "",
        "canonical_url": f"https://{domain}{path}",
        "robots": "index,follow",
        "og_title": title,
        "og_description": description,
        "og_image": "",
        "twitter_title": title,
        "twitter_description": description,
        "twitter_image": "",
        "schema_json": "",
    }


@router.post("/contact", name="contact-submit")
def submit_contact(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    company_name: str = Form(""),
    subject: str = Form(""),
    message: str = Form(...),
    service_interest: str = Form(""),
    source_page: str = Form("/contact"),
    db: Session = Depends(get_database),
):
    form_input = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "subject": subject,
        "message": message,
        "service_interest": service_interest,
        "source_page": source_page,
    }
    result = ContactForm.validate(form_input)
    if not result.is_valid:
        return templates.TemplateResponse(
            "public/contact.html",
            {
                "request": request,
                **_meta_defaults(
                    "Contact",
                    "Contact NeuralShield Digital to discuss AI consulting, product builds, automation, and custom software solutions.",
                    "/contact",
                    request.app.state.settings.domain,
                ),
                "form_data": form_input,
                "form_errors": result.errors,
                "form_success": False,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    payload = ContactSubmissionCreate(**result.cleaned_data)
    ContactLeadService(db).create_lead(payload)
    return RedirectResponse("/contact?submitted=1", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/book-consultation", name="book-consultation-submit")
def submit_consultation(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(""),
    company_name: str = Form(""),
    consultation_type: str = Form("strategy"),
    preferred_datetime: str = Form(""),
    timezone: str = Form("Asia/Calcutta"),
    project_details: str = Form(...),
    db: Session = Depends(get_database),
):
    form_input = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "company_name": company_name,
        "consultation_type": consultation_type,
        "preferred_datetime": preferred_datetime or None,
        "timezone": timezone,
        "project_details": project_details,
        
    }
    print("BOOKING FORM INPUT:", form_input)
    result = ConsultationBookingForm.validate(form_input)
    print("BOOKING VALID:", result.is_valid)
    print("BOOKING ERRORS:", result.errors)
    if not result.is_valid:
        return templates.TemplateResponse(
            "public/consultation.html",
            {
                "request": request,
                **_meta_defaults(
                    "Book Consultation",
                    "Book an AI strategy or technical consultation with NeuralShield Digital.",
                    "/book-consultation",
                    request.app.state.settings.domain,
                ),
                "form_data": form_input,
                "form_errors": result.errors,
                "form_success": False,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    payload = ConsultationBookingCreate(**result.cleaned_data)
    ConsultationBookingService(db).create_booking(payload)
    return RedirectResponse("/book-consultation?submitted=1", status_code=status.HTTP_303_SEE_OTHER)
