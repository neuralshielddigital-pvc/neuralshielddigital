from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost
from app.models.consultation_booking import ConsultationBooking
from app.models.contact_lead import ContactLead
from app.models.product import Product
from app.models.service import Service
from app.models.testimonial import Testimonial
from app.routers.deps import get_database, require_admin


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin", tags=["admin-dashboard"])


@router.get("", response_class=HTMLResponse, name="admin-root")
@router.get("/dashboard", response_class=HTMLResponse, name="admin-dashboard")
def dashboard(request: Request, db: Session = Depends(get_database)):
    admin = request.session.get("admin")

    summary = {
        "total_leads": db.scalar(select(func.count()).select_from(ContactLead)) or 0,
        "new_leads": db.scalar(select(func.count()).select_from(ContactLead)) or 0,
        "total_bookings": db.scalar(select(func.count()).select_from(ConsultationBooking)) or 0,
        "pending_bookings": db.scalar(select(func.count()).select_from(ConsultationBooking)) or 0,
    }

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "admin": admin,
            "page_title": "Dashboard",
            "summary": summary,
            **summary,
        },
    )
    recent_leads = list(db.scalars(select(ContactLead).order_by(ContactLead.created_at.desc()).limit(5)))
    recent_bookings = list(db.scalars(select(ConsultationBooking).order_by(ConsultationBooking.created_at.desc()).limit(5)))
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "page_title": "Dashboard",
            "summary": summary,
            "recent_leads": recent_leads,
            "recent_bookings": recent_bookings,
            "admin": admin,
        },
    )
