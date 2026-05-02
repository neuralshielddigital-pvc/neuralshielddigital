from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.blog_post import BlogPost
from app.models.page_seo import PageSEO
from app.routers.deps import get_database
from app.services.blog_management_service import BlogManagementService
from app.utils.seo import build_metadata, build_sitemap_entries


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(tags=["public-blog"])

@router.get("/blog", response_class=HTMLResponse, name="blog-list")
def blog_index(request: Request, db: Session = Depends(get_database)):
    posts = list(
        db.scalars(
            select(BlogPost)
            .options(selectinload(BlogPost.category))
            .where(BlogPost.status == "published")
            .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc())
        )
    )
    categories = BlogManagementService(db).list_categories()
    return templates.TemplateResponse(
        "public/blog_list.html",
        {
            "request": request,
            **build_metadata(
                request=request,
                db=db,
                page_title="Blog",
                page_path="/blog",
                fallback_description="Insights from NeuralShield Digital on AI, LLMs, machine learning, automation, DevOps, and applied engineering.",
            ),
            "posts": posts,
            "categories": categories,
        },
    )


@router.get("/blog/{slug}", response_class=HTMLResponse, name="blog-detail")
def blog_detail(slug: str, request: Request, db: Session = Depends(get_database)):
    post = db.scalar(
        select(BlogPost)
        .options(selectinload(BlogPost.category), selectinload(BlogPost.author))
        .where(BlogPost.slug == slug, BlogPost.status == "published")
    )
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Blog post not found.")

    seo = db.scalar(select(PageSEO).where(PageSEO.page_type == "blog_post", PageSEO.object_id == post.id))
    related_posts = list(
        db.scalars(
            select(BlogPost)
            .where(BlogPost.status == "published", BlogPost.id != post.id)
            .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc())
            .limit(3)
        )
    )

    return templates.TemplateResponse(
        "public/blog_detail.html",
        {
            "request": request,
            **build_metadata(
                request=request,
                db=db,
                page_title=post.title,
                page_path=f"/blog/{post.slug}",
                fallback_description=post.excerpt or post.title,
                seo=seo,
            ),
            "post": post,
            "related_posts": related_posts,
            "slug": slug,
        },
    )


@router.get("/sitemap.xml", response_class=HTMLResponse, name="sitemap")
def sitemap(request: Request, db: Session = Depends(get_database)):
    domain = request.app.state.settings.domain
    entries = build_sitemap_entries(db, domain)
    xml = templates.get_template("public/sitemap.xml").render(
        {
            "request": request,
            "entries": entries,
        }
    )
    return HTMLResponse(content=xml, media_type="application/xml")
