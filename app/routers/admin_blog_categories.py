from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routers.deps import get_database, require_admin
from app.schemas.blog import BlogCategoryCreate, BlogCategoryUpdate
from app.services.base import ConflictError
from app.services.blog_management_service import BlogManagementService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/blog/categories", tags=["admin-blog-categories"])


@router.get("", response_class=HTMLResponse, name="admin-blog-categories-list")
def categories_index(request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    categories = BlogManagementService(db).list_categories()
    return templates.TemplateResponse(
        "admin/blog_categories/index.html",
        {"request": request, "page_title": "Blog Categories", "admin": admin, "categories": categories, "form_errors": {}, "form_data": {"name": "", "slug": "", "description": ""}},
    )


@router.post("/create", name="admin-blog-categories-create")
def category_create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = BlogCategoryCreate(name=name, slug=slug, description=description or None)
    try:
        BlogManagementService(db).create_category(payload)
    except ConflictError as exc:
        categories = BlogManagementService(db).list_categories()
        return templates.TemplateResponse(
            "admin/blog_categories/index.html",
            {"request": request, "page_title": "Blog Categories", "admin": admin, "categories": categories, "form_errors": {"slug": [str(exc)]}, "form_data": payload.model_dump()},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/blog/categories", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{category_id}/edit", name="admin-blog-categories-edit")
def category_edit(
    category_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    description: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    _ = admin
    BlogManagementService(db).update_category(category_id, BlogCategoryUpdate(name=name, slug=slug, description=description or None))
    return RedirectResponse("/admin/blog/categories", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{category_id}/delete", name="admin-blog-categories-delete")
def category_delete(category_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    category = BlogManagementService(db).get_category(category_id)
    db.delete(category)
    db.commit()
    return RedirectResponse("/admin/blog/categories", status_code=status.HTTP_303_SEE_OTHER)
