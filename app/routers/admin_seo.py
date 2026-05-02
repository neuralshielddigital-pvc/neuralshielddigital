from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.page_seo import PageSEO
from app.routers.deps import get_database, require_admin
from app.schemas.seo import PageSEOCreate, PageSEOUpdate
from app.services.base import ConflictError
from app.services.seo_metadata_service import SEOMetadataService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/seo", tags=["admin-seo"])
PAGE_SIZE = 10


def _seo_form_data(item: PageSEO | None = None) -> dict:
    if item:
        return {
            "page_key": item.page_key,
            "page_type": item.page_type,
            "object_id": item.object_id or "",
            "page_path": item.page_path,
            "meta_title": item.meta_title or "",
            "meta_description": item.meta_description or "",
            "meta_keywords": item.meta_keywords or "",
            "canonical_url": item.canonical_url or "",
            "robots": item.robots,
            "og_title": item.og_title or "",
            "og_description": item.og_description or "",
            "og_image": item.og_image or "",
            "twitter_title": item.twitter_title or "",
            "twitter_description": item.twitter_description or "",
            "twitter_image": item.twitter_image or "",
            "schema_json": item.schema_json or "",
        }
    return {
        "page_key": "",
        "page_type": "page",
        "object_id": "",
        "page_path": "",
        "meta_title": "",
        "meta_description": "",
        "meta_keywords": "",
        "canonical_url": "",
        "robots": "index,follow",
        "og_title": "",
        "og_description": "",
        "og_image": "",
        "twitter_title": "",
        "twitter_description": "",
        "twitter_image": "",
        "schema_json": "",
    }


@router.get("", response_class=HTMLResponse, name="admin-seo-list")
def seo_index(request: Request, q: str = Query(default=""), page: int = Query(default=1, ge=1), db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    query = select(PageSEO)
    count_query = select(func.count()).select_from(PageSEO)
    if q:
        search_filter = or_(PageSEO.page_key.ilike(f"%{q}%"), PageSEO.page_path.ilike(f"%{q}%"), PageSEO.page_type.ilike(f"%{q}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    items = list(db.scalars(query.order_by(PageSEO.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
    return templates.TemplateResponse(
        "admin/seo/index.html",
        {"request": request, "page_title": "SEO Metadata", "admin": admin, "items": items, "search_query": q, "page": page, "total_pages": max(ceil(total / PAGE_SIZE), 1)},
    )


@router.get("/create", response_class=HTMLResponse, name="admin-seo-create")
def seo_create_page(request: Request, admin: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/seo/form.html",
        {"request": request, "page_title": "Create SEO Metadata", "admin": admin, "item": None, "form_data": _seo_form_data(), "form_errors": {}},
    )


@router.post("/create", name="admin-seo-create-submit")
def seo_create_submit(
    request: Request,
    page_key: str = Form(...),
    page_type: str = Form(...),
    object_id: str = Form(""),
    page_path: str = Form(...),
    meta_title: str = Form(""),
    meta_description: str = Form(""),
    meta_keywords: str = Form(""),
    canonical_url: str = Form(""),
    robots: str = Form("index,follow"),
    og_title: str = Form(""),
    og_description: str = Form(""),
    og_image: str = Form(""),
    twitter_title: str = Form(""),
    twitter_description: str = Form(""),
    twitter_image: str = Form(""),
    schema_json: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = PageSEOCreate(
        page_key=page_key,
        page_type=page_type,
        object_id=int(object_id) if object_id else None,
        page_path=page_path,
        meta_title=meta_title or None,
        meta_description=meta_description or None,
        meta_keywords=meta_keywords or None,
        canonical_url=canonical_url or None,
        robots=robots,
        og_title=og_title or None,
        og_description=og_description or None,
        og_image=og_image or None,
        twitter_title=twitter_title or None,
        twitter_description=twitter_description or None,
        twitter_image=twitter_image or None,
        schema_json=schema_json or None,
    )
    try:
        SEOMetadataService(db).create_metadata(payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/seo/form.html",
            {"request": request, "page_title": "Create SEO Metadata", "admin": admin, "item": None, "form_data": payload.model_dump(), "form_errors": {"page_key": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/seo", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{seo_id}/edit", response_class=HTMLResponse, name="admin-seo-edit")
def seo_edit_page(seo_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    item = SEOMetadataService(db).get_metadata(seo_id)
    return templates.TemplateResponse(
        "admin/seo/form.html",
        {"request": request, "page_title": f"Edit SEO {item.page_key}", "admin": admin, "item": item, "form_data": _seo_form_data(item), "form_errors": {}},
    )


@router.post("/{seo_id}/edit", name="admin-seo-edit-submit")
def seo_edit_submit(
    seo_id: int,
    request: Request,
    page_key: str = Form(...),
    page_type: str = Form(...),
    object_id: str = Form(""),
    page_path: str = Form(...),
    meta_title: str = Form(""),
    meta_description: str = Form(""),
    meta_keywords: str = Form(""),
    canonical_url: str = Form(""),
    robots: str = Form("index,follow"),
    og_title: str = Form(""),
    og_description: str = Form(""),
    og_image: str = Form(""),
    twitter_title: str = Form(""),
    twitter_description: str = Form(""),
    twitter_image: str = Form(""),
    schema_json: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = PageSEOUpdate(
        page_key=page_key,
        page_type=page_type,
        object_id=int(object_id) if object_id else None,
        page_path=page_path,
        meta_title=meta_title or None,
        meta_description=meta_description or None,
        meta_keywords=meta_keywords or None,
        canonical_url=canonical_url or None,
        robots=robots,
        og_title=og_title or None,
        og_description=og_description or None,
        og_image=og_image or None,
        twitter_title=twitter_title or None,
        twitter_description=twitter_description or None,
        twitter_image=twitter_image or None,
        schema_json=schema_json or None,
    )
    item = SEOMetadataService(db).get_metadata(seo_id)
    try:
        SEOMetadataService(db).update_metadata(seo_id, payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/seo/form.html",
            {"request": request, "page_title": f"Edit SEO {item.page_key}", "admin": admin, "item": item, "form_data": payload.model_dump(exclude_none=False), "form_errors": {"page_key": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/seo", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{seo_id}/delete", name="admin-seo-delete")
def seo_delete(seo_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    SEOMetadataService(db).delete_metadata(seo_id)
    return RedirectResponse("/admin/seo", status_code=status.HTTP_303_SEE_OTHER)
