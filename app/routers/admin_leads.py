from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.contact_lead import ContactLead
from app.routers.deps import get_database, require_admin
from app.schemas.contact import ContactLeadUpdate
from app.services.base import NotFoundError
from app.services.contact_lead_service import ContactLeadService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/leads", tags=["admin-leads"])
PAGE_SIZE = 10


@router.get("", response_class=HTMLResponse, name="admin-leads-list")

def leads_index(
    request: Request,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_database),
):
    admin = request.session.get("admin")
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)
    query = select(ContactLead)
    count_query = select(func.count()).select_from(ContactLead)
    if q:
        search_filter = or_(
            ContactLead.full_name.ilike(f"%{q}%"),
            ContactLead.email.ilike(f"%{q}%"),
            ContactLead.company_name.ilike(f"%{q}%"),
            ContactLead.subject.ilike(f"%{q}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    leads = list(
        db.scalars(
            query.order_by(ContactLead.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)
        )
    )
    return templates.TemplateResponse(
        "admin/leads/index.html",
        {
            "request": request,
            "page_title": "Leads",
            "admin": admin,
            "leads": leads,
            "search_query": q,
            "page": page,
            "total_pages": max(ceil(total / PAGE_SIZE), 1),
            "total": total,
        },
    )


@router.get("/{lead_id}", response_class=HTMLResponse, name="admin-leads-detail")
def lead_detail(lead_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    lead = ContactLeadService(db).get_lead(lead_id)
    return templates.TemplateResponse(
        "admin/leads/detail.html",
        {"request": request, "page_title": f"Lead #{lead.id}", "lead": lead, "admin": admin, "form_errors": {}},
    )


@router.post("/{lead_id}/update", name="admin-leads-update")
def lead_update(
    lead_id: int,
    request: Request,
    status_value: str = Form(..., alias="status"),
    priority: str = Form("normal"),
    notes: str = Form(""),
    budget_range: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    _ = request, admin
    ContactLeadService(db).update_lead(
        lead_id,
        ContactLeadUpdate(status=status_value, priority=priority, notes=notes, budget_range=budget_range),
    )
    return RedirectResponse(f"/admin/leads/{lead_id}", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{lead_id}/delete", name="admin-leads-delete")
def lead_delete(lead_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    ContactLeadService(db).delete_lead(lead_id)
    return RedirectResponse("/admin/leads", status_code=status.HTTP_303_SEE_OTHER)
