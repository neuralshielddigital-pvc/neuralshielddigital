from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.testimonial import Testimonial
from app.routers.deps import get_database, require_admin
from app.schemas.testimonial import TestimonialCreate, TestimonialUpdate
from app.services.testimonial_management_service import TestimonialManagementService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/testimonials", tags=["admin-testimonials"])
PAGE_SIZE = 10


def _testimonial_form_data(testimonial: Testimonial | None = None) -> dict:
    if testimonial:
        return {
            "client_name": testimonial.client_name,
            "company_name": testimonial.company_name or "",
            "designation": testimonial.designation or "",
            "testimonial_text": testimonial.testimonial_text,
            "rating": testimonial.rating,
            "is_featured": testimonial.is_featured,
            "display_order": testimonial.display_order,
            "source_url": testimonial.source_url or "",
            "is_active": testimonial.is_active,
        }
    return {
        "client_name": "",
        "company_name": "",
        "designation": "",
        "testimonial_text": "",
        "rating": 5,
        "is_featured": False,
        "display_order": 0,
        "source_url": "",
        "is_active": True,
    }


@router.get("", response_class=HTMLResponse, name="admin-testimonials-list")
def testimonials_index(request: Request, q: str = Query(default=""), page: int = Query(default=1, ge=1), db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    query = select(Testimonial)
    count_query = select(func.count()).select_from(Testimonial)
    if q:
        search_filter = or_(Testimonial.client_name.ilike(f"%{q}%"), Testimonial.company_name.ilike(f"%{q}%"), Testimonial.designation.ilike(f"%{q}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    testimonials = list(db.scalars(query.order_by(Testimonial.display_order.asc(), Testimonial.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
    return templates.TemplateResponse(
        "admin/testimonials/index.html",
        {"request": request, "page_title": "Testimonials", "admin": admin, "testimonials": testimonials, "search_query": q, "page": page, "total_pages": max(ceil(total / PAGE_SIZE), 1)},
    )


@router.get("/create", response_class=HTMLResponse, name="admin-testimonials-create")
def testimonial_create_page(request: Request, admin: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/testimonials/form.html",
        {"request": request, "page_title": "Create Testimonial", "admin": admin, "testimonial": None, "form_data": _testimonial_form_data(), "form_errors": {}},
    )


@router.post("/create", name="admin-testimonials-create-submit")
def testimonial_create_submit(
    client_name: str = Form(...),
    company_name: str = Form(""),
    designation: str = Form(""),
    testimonial_text: str = Form(...),
    rating: int = Form(5),
    is_featured: bool = Form(False),
    display_order: int = Form(0),
    source_url: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    _ = admin
    payload = TestimonialCreate(
        client_name=client_name,
        company_name=company_name or None,
        designation=designation or None,
        testimonial_text=testimonial_text,
        rating=rating,
        is_featured=is_featured,
        display_order=display_order,
        source_url=source_url or None,
        is_active=is_active,
    )
    TestimonialManagementService(db).create_testimonial(payload)
    return RedirectResponse("/admin/testimonials", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{testimonial_id}/edit", response_class=HTMLResponse, name="admin-testimonials-edit")
def testimonial_edit_page(testimonial_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    testimonial = TestimonialManagementService(db).get_testimonial(testimonial_id)
    return templates.TemplateResponse(
        "admin/testimonials/form.html",
        {"request": request, "page_title": f"Edit {testimonial.client_name}", "admin": admin, "testimonial": testimonial, "form_data": _testimonial_form_data(testimonial), "form_errors": {}},
    )


@router.post("/{testimonial_id}/edit", name="admin-testimonials-edit-submit")
def testimonial_edit_submit(
    testimonial_id: int,
    client_name: str = Form(...),
    company_name: str = Form(""),
    designation: str = Form(""),
    testimonial_text: str = Form(...),
    rating: int = Form(5),
    is_featured: bool = Form(False),
    display_order: int = Form(0),
    source_url: str = Form(""),
    is_active: bool = Form(False),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    _ = admin
    payload = TestimonialUpdate(
        client_name=client_name,
        company_name=company_name or None,
        designation=designation or None,
        testimonial_text=testimonial_text,
        rating=rating,
        is_featured=is_featured,
        display_order=display_order,
        source_url=source_url or None,
        is_active=is_active,
    )
    TestimonialManagementService(db).update_testimonial(testimonial_id, payload)
    return RedirectResponse("/admin/testimonials", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{testimonial_id}/delete", name="admin-testimonials-delete")
def testimonial_delete(testimonial_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    TestimonialManagementService(db).delete_testimonial(testimonial_id)
    return RedirectResponse("/admin/testimonials", status_code=status.HTTP_303_SEE_OTHER)
