from __future__ import annotations

from math import ceil
from pathlib import Path

from fastapi import APIRouter, Depends, Form, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost
from app.routers.deps import get_database, require_admin
from app.schemas.blog import BlogPostCreate, BlogPostUpdate
from app.services.base import ConflictError
from app.services.blog_management_service import BlogManagementService


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin/blog", tags=["admin-blog-posts"])
PAGE_SIZE = 10


def _post_form_data(post: BlogPost | None = None) -> dict:
    if post:
        return {
            "category_id": post.category_id or "",
            "author_id": post.author_id or "",
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt or "",
            "featured_image": post.featured_image or "",
            "content_markdown": post.content_markdown,
            "content_html": post.content_html or "",
            "status": post.status,
            "is_featured": post.is_featured,
            "published_at": post.published_at.isoformat() if post.published_at else "",
        }
    return {
        "category_id": "",
        "author_id": "",
        "title": "",
        "slug": "",
        "excerpt": "",
        "featured_image": "",
        "content_markdown": "",
        "content_html": "",
        "status": "draft",
        "is_featured": False,
        "published_at": "",
    }


@router.get("", response_class=HTMLResponse, name="admin-blog-posts-list")
def blog_index(request: Request, q: str = Query(default=""), page: int = Query(default=1, ge=1), db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    query = select(BlogPost)
    count_query = select(func.count()).select_from(BlogPost)
    if q:
        search_filter = or_(BlogPost.title.ilike(f"%{q}%"), BlogPost.slug.ilike(f"%{q}%"), BlogPost.excerpt.ilike(f"%{q}%"))
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)
    total = db.scalar(count_query) or 0
    posts = list(db.scalars(query.order_by(BlogPost.created_at.desc()).offset((page - 1) * PAGE_SIZE).limit(PAGE_SIZE)))
    return templates.TemplateResponse(
        "admin/blog/index.html",
        {"request": request, "page_title": "Blog Posts", "admin": admin, "posts": posts, "search_query": q, "page": page, "total_pages": max(ceil(total / PAGE_SIZE), 1)},
    )


@router.get("/create", response_class=HTMLResponse, name="admin-blog-posts-create")
def blog_create_page(request: Request, db: Session = Depends(get_database), 
                     
admin: dict = Depends(require_admin)):
    categories = BlogManagementService(db).list_categories()
    return templates.TemplateResponse(
        "admin/blog/form.html",
        {"request": request, "page_title": "Create Blog Post", "admin": admin, "post": None, "categories": categories, "form_data": _post_form_data(), "form_errors": {}},
    )


@router.post("/create", name="admin-blog-posts-create-submit")
def blog_create_submit(
    request: Request,
    category_id: str = Form(""),
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(""),
    featured_image: str = Form(""),
    content_markdown: str = Form(...),
    content_html: str = Form(""),
    status_value: str = Form("draft", alias="status"),
    is_featured: bool = Form(False),
    published_at: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = BlogPostCreate(
        category_id=int(category_id) if category_id else None,
        author_id=admin["id"],
        title=title,
        slug=slug,
        excerpt=excerpt or None,
        featured_image=featured_image or None,
        content_markdown=content_markdown,
        content_html=content_html or None,
        status=status_value,
        is_featured=is_featured,
        published_at=published_at or None,
    )
    try:
        BlogManagementService(db).create_post(payload)
    except ConflictError as exc:
        categories = BlogManagementService(db).list_categories()
        return templates.TemplateResponse(
            "admin/blog/form.html",
            {"request": request, "page_title": "Create Blog Post", "admin": admin, "post": None, "categories": categories, "form_data": payload.model_dump(), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/blog", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/{post_id}/edit", response_class=HTMLResponse, name="admin-blog-posts-edit")
def blog_edit_page(post_id: int, request: Request, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    post = BlogManagementService(db).get_post(post_id)
    categories = BlogManagementService(db).list_categories()
    return templates.TemplateResponse(
        "admin/blog/form.html",
        {"request": request, "page_title": f"Edit {post.title}", "admin": admin, "post": post, "categories": categories, "form_data": _post_form_data(post), "form_errors": {}},
    )


@router.post("/{post_id}/edit", name="admin-blog-posts-edit-submit")
def blog_edit_submit(
    post_id: int,
    request: Request,
    category_id: str = Form(""),
    title: str = Form(...),
    slug: str = Form(...),
    excerpt: str = Form(""),
    featured_image: str = Form(""),
    content_markdown: str = Form(...),
    content_html: str = Form(""),
    status_value: str = Form("draft", alias="status"),
    is_featured: bool = Form(False),
    published_at: str = Form(""),
    db: Session = Depends(get_database),
    admin: dict = Depends(require_admin),
):
    payload = BlogPostUpdate(
        category_id=int(category_id) if category_id else None,
        author_id=admin["id"],
        title=title,
        slug=slug,
        excerpt=excerpt or None,
        featured_image=featured_image or None,
        content_markdown=content_markdown,
        content_html=content_html or None,
        status=status_value,
        is_featured=is_featured,
        published_at=published_at or None,
    )
    post = BlogManagementService(db).get_post(post_id)
    try:
        BlogManagementService(db).update_post(post_id, payload)
    except ConflictError as exc:
        categories = BlogManagementService(db).list_categories()
        return templates.TemplateResponse(
            "admin/blog/form.html",
            {"request": request, "page_title": f"Edit {post.title}", "admin": admin, "post": post, "categories": categories, "form_data": payload.model_dump(exclude_none=False), "form_errors": {"slug": [str(exc)]}},
            status_code=status.HTTP_409_CONFLICT,
        )
    return RedirectResponse("/admin/blog", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/{post_id}/delete", name="admin-blog-posts-delete")
def blog_delete(post_id: int, db: Session = Depends(get_database), admin: dict = Depends(require_admin)):
    _ = admin
    BlogManagementService(db).delete_post(post_id)
    return RedirectResponse("/admin/blog", status_code=status.HTTP_303_SEE_OTHER)
