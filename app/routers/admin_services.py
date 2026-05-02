from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.service import Service
from app.routers.deps import get_database, require_admin
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.base import ConflictError
from app.services.service_management_service import ServiceManagementService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/services", tags=["admin-services"])
PAGE_SIZE = 10


def _service_form_data(service: Service | None = None) -> dict:
    if service:
        return {
            "name": service.name,
            "slug": service.slug,
            "tagline": service.tagline or "",
            "short_description": service.short_description,
            "full_description": service.full_description,
            "icon_name": service.icon_name or "",
            "hero_title": service.hero_title or "",
            "hero_subtitle": service.hero_subtitle or "",
            "cta_label": service.cta_label or "",
            "cta_url": service.cta_url or "",
            "display_order": service.display_order,
            "is_active": service.is_active,
            "is_featured": service.is_featured,
        }
    return {
        "name": "",
        "slug": "",
        "tagline": "",
        "short_description": "",
        "full_description": "",
        "icon_name": "",
        "hero_title": "",
        "hero_subtitle": "",
        "cta_label": "",
        "cta_url": "",
        "display_order": 0,
        "is_active": True,
        "is_featured": False,
    }


@router.get("", response_class=HTMLResponse, name="admin-services-list")
def services_index(
    request: Request,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    admin = request.session.get("admin")
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)
    query = select(Service)
    count_query = select(func.count()).select_from(Service)
    if q:
        search_filter = or_(Service.name.ilike(f"%{q}%"), Service.slug.ilike(f"%{q}%"), Service.short_description.ilike(f"%{q}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    services = list(db.scalars(query.order_by(Service.display_order.asc(), Service.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
    return templates.TemplateResponse(
        "admin/services/index.html",
        {"request": request, "page_title": "Services", "admin": admin, "services": services, "search_query": q, "page": page, "total_pages": max(ceil(total / PAGE_SIZE), 1)},
    )


@router.get("/create", response_class=HTMLResponse, name="admin-services-create")
def service_create_page(request: Request, admin: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/services/form.html",
        {"request": request, "page_title": "Create Service", "admin": admin, "service": None, "form_data": _service_form_data(), "form_errors": {}},
    )


@router.post("/create", name="admin-services-create-submit")
def service_create_submit(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    tagline: str = Form(""),
    short_description: str = Form(...),
    full_description: str = Form(...),
    icon_name: str = Form(""),
    hero_title: str = Form(""),
    hero_subtitle: str = Form(""),
    cta_label: str = Form(""),
    cta_url: str = Form(""),
    display_order: int = Form(0),
    is_active: bool = Form(False),
    is_featured: bool = Form(False),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = ServiceCreate(
        name=name,
        slug=slug,
        tagline=tagline or None,
        short_description=short_description,
        full_description=full_description,
        icon_name=icon_name or None,
        hero_title=hero_title or None,
        hero_subtitle=hero_subtitle or None,
        cta_label=cta_label or None,
        cta_url=cta_url or None,
        display_order=display_order,
        is_active=is_active,
        is_featured=is_featured,
    )
    try:
        ServiceManagementService(db).create_service(payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/services/form.html",
            {"request": request, "page_title": "Create Service", "admin": admin, "service": None, "form_data": payload.model_dump(), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/services", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{service_id}/edit", response_class=HTMLResponse, name="admin-services-edit")
def service_edit_page(service_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    service = ServiceManagementService(db).get_service(service_id)
    return templates.TemplateResponse(
        "admin/services/form.html",
        {"request": request, "page_title": f"Edit {service.name}", "admin": admin, "service": service, "form_data": _service_form_data(service), "form_errors": {}},
    )


@router.post("/{service_id}/edit", name="admin-services-edit-submit")
def service_edit_submit(
    service_id: int,
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    tagline: str = Form(""),
    short_description: str = Form(...),
    full_description: str = Form(...),
    icon_name: str = Form(""),
    hero_title: str = Form(""),
    hero_subtitle: str = Form(""),
    cta_label: str = Form(""),
    cta_url: str = Form(""),
    display_order: int = Form(0),
    is_active: bool = Form(False),
    is_featured: bool = Form(False),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = ServiceUpdate(
        name=name,
        slug=slug,
        tagline=tagline or None,
        short_description=short_description,
        full_description=full_description,
        icon_name=icon_name or None,
        hero_title=hero_title or None,
        hero_subtitle=hero_subtitle or None,
        cta_label=cta_label or None,
        cta_url=cta_url or None,
        display_order=display_order,
        is_active=is_active,
        is_featured=is_featured,
    )
    service = ServiceManagementService(db).get_service(service_id)
    try:
        ServiceManagementService(db).update_service(service_id, payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/services/form.html",
            {"request": request, "page_title": f"Edit {service.name}", "admin": admin, "service": service, "form_data": payload.model_dump(exclude_none=False), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/services", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{service_id}/delete", name="admin-services-delete")
def service_delete(service_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    ServiceManagementService(db).delete_service(service_id)
    return RedirectResponse("/admin/services", status_code=status.HTTP_303_SEE_OTHER)
