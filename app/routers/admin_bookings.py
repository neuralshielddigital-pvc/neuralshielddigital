from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.consultation_booking import ConsultationBooking
from app.routers.deps import get_database, require_admin
from app.schemas.booking import ConsultationBookingUpdate
from app.services.consultation_booking_service import ConsultationBookingService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/bookings", tags=["admin-bookings"])
PAGE_SIZE = 10


@router.get("", response_class=HTMLResponse, name="admin-bookings-list")
def bookings_index(
    request: Request,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_database),
):
    admin = request.session.get("admin")
    # baaki code yahin continue hoga
    query = select(ConsultationBooking)
    count_query = select(func.count()).select_from(ConsultationBooking)
    if q:
        search_filter = or_(
            ConsultationBooking.full_name.ilike(f"%{q}%"),
            ConsultationBooking.email.ilike(f"%{q}%"),
            ConsultationBooking.company_name.ilike(f"%{q}%"),
            ConsultationBooking.consultation_type.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    bookings = list(
        db.scalars(
            query.order_by(ConsultationBooking.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
        )
    )
    return templates.TemplateResponse(
        "admin/bookings/index.html",
        {
            "request": request,
            "page_title": "Consultation Bookings",
            "admin": admin,
            "bookings": bookings,
            "search_query": q,
            "page": page,
            "total_pages": max(ceil(total / PAGE_SIZE), 1),
            "total": total,
        },
    )


@router.get("/{booking_id}", response_class=HTMLResponse, name="admin-bookings-detail")
def booking_detail(booking_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    booking = ConsultationBookingService(db).get_booking(booking_id)
    return templates.TemplateResponse(
        "admin/bookings/detail.html",
        {"request": request, "page_title": f"Booking #{booking.id}", "booking": booking, "admin": admin},
    )


@router.post("/{booking_id}/update", name="admin-bookings-update")
def booking_update(
    booking_id: int,
    status_value: str = Form(..., alias="status"),
    meeting_link: str = Form(""),
    admin_notes: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    _ = admin
    ConsultationBookingService(db).update_booking(
        booking_id,
        ConsultationBookingUpdate(status=status_value, meeting_link=meeting_link, admin_notes=admin_notes),
    )
    return RedirectResponse(f"/admin/bookings/{booking_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{booking_id}/delete", name="admin-bookings-delete")
def booking_delete(booking_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    ConsultationBookingService(db).delete_booking(booking_id)
    return RedirectResponse("/admin/bookings", status_code=status.HTTP_303_SEE_OTHER)
