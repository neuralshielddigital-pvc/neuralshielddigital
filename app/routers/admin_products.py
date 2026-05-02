from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.routers.deps import get_database, require_admin
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.base import ConflictError
from app.services.product_management_service import ProductManagementService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/products", tags=["admin-products"])
PAGE_SIZE = 10


def _product_form_data(product: Product | None = None) -> dict:
    if product:
        return {
            "name": product.name,
            "slug": product.slug,
            "tagline": product.tagline or "",
            "short_description": product.short_description,
            "full_description": product.full_description,
            "product_type": product.product_type,
            "status": product.status,
            "website_url": product.website_url or "",
            "cta_label": product.cta_label or "",
            "cta_url": product.cta_url or "",
            "pricing_summary": product.pricing_summary or "",
            "display_order": product.display_order,
            "is_featured": product.is_featured,
            "published_at": product.published_at.isoformat() if product.published_at else "",
        }
    return {
        "name": "",
        "slug": "",
        "tagline": "",
        "short_description": "",
        "full_description": "",
        "product_type": "platform",
        "status": "draft",
        "website_url": "",
        "cta_label": "",
        "cta_url": "",
        "pricing_summary": "",
        "display_order": 0,
        "is_featured": False,
        "published_at": "",
    }


@router.get("", response_class=HTMLResponse, name="admin-products-list")
def products_index(request: Request, q: str = Query(default=""), page: int = Query(default=1, ge=1), db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    query = select(Product)
    admin = request.session.get("admin")
    if not admin:
        return RedirectResponse(url="/admin/login", status_code=302)
    count_query = select(func.count()).select_from(Product)
    if q:
        search_filter = or_(Product.name.ilike(f"%{q}%"), Product.slug.ilike(f"%{q}%"), Product.short_description.ilike(f"%{q}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    products = list(db.scalars(query.order_by(Product.display_order.asc(), Product.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
    return templates.TemplateResponse(
        "admin/products/index.html",
        {"request": request, "page_title": "Products", "admin": admin, "products": products, "search_query": q, "page": page, "total_pages": max(ceil(total / PAGE_SIZE), 1)},
    )


@router.get("/create", response_class=HTMLResponse, name="admin-products-create")
def product_create_page(request: Request, admin: dict = Depends(require_admin)):
    return templates.TemplateResponse(
        "admin/products/form.html",
        {"request": request, "page_title": "Create Product", "admin": admin, "product": None, "form_data": _product_form_data(), "form_errors": {}},
    )


@router.post("/create", name="admin-products-create-submit")
def product_create_submit(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    tagline: str = Form(""),
    short_description: str = Form(...),
    full_description: str = Form(...),
    product_type: str = Form("platform"),
    status_value: str = Form("draft", alias="status"),
    website_url: str = Form(""),
    cta_label: str = Form(""),
    cta_url: str = Form(""),
    pricing_summary: str = Form(""),
    display_order: int = Form(0),
    is_featured: bool = Form(False),
    published_at: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = ProductCreate(
        name=name,
        slug=slug,
        tagline=tagline or None,
        short_description=short_description,
        full_description=full_description,
        product_type=product_type,
        status=status_value,
        website_url=website_url or None,
        cta_label=cta_label or None,
        cta_url=cta_url or None,
        pricing_summary=pricing_summary or None,
        display_order=display_order,
        is_featured=is_featured,
        published_at=published_at or None,
    )
    try:
        ProductManagementService(db).create_product(payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/products/form.html",
            {"request": request, "page_title": "Create Product", "admin": admin, "product": None, "form_data": payload.model_dump(), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/products", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{product_id}/edit", response_class=HTMLResponse, name="admin-products-edit")
def product_edit_page(product_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    product = ProductManagementService(db).get_product(product_id)
    return templates.TemplateResponse(
        "admin/products/form.html",
        {"request": request, "page_title": f"Edit {product.name}", "admin": admin, "product": product, "form_data": _product_form_data(product), "form_errors": {}},
    )


@router.post("/{product_id}/edit", name="admin-products-edit-submit")
def product_edit_submit(
    product_id: int,
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    tagline: str = Form(""),
    short_description: str = Form(...),
    full_description: str = Form(...),
    product_type: str = Form("platform"),
    status_value: str = Form("draft", alias="status"),
    website_url: str = Form(""),
    cta_label: str = Form(""),
    cta_url: str = Form(""),
    pricing_summary: str = Form(""),
    display_order: int = Form(0),
    is_featured: bool = Form(False),
    published_at: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = ProductUpdate(
        name=name,
        slug=slug,
        tagline=tagline or None,
        short_description=short_description,
        full_description=full_description,
        product_type=product_type,
        status=status_value,
        website_url=website_url or None,
        cta_label=cta_label or None,
        cta_url=cta_url or None,
        pricing_summary=pricing_summary or None,
        display_order=display_order,
        is_featured=is_featured,
        published_at=published_at or None,
    )
    product = ProductManagementService(db).get_product(product_id)
    try:
        ProductManagementService(db).update_product(product_id, payload)
    except ConflictError as exc:
        return templates.TemplateResponse(
            "admin/products/form.html",
            {"request": request, "page_title": f"Edit {product.name}", "admin": admin, "product": product, "form_data": payload.model_dump(exclude_none=False), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/products", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{product_id}/delete", name="admin-products-delete")
def product_delete(product_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    ProductManagementService(db).delete_product(product_id)
    return RedirectResponse("/admin/products", status_code=status.HTTP_303_SEE_OTHER)
