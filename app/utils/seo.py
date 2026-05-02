from __future__ import annotations

from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost
from app.models.case_study import CaseStudy
from app.models.page_seo import PageSEO
from app.models.product import Product
from app.models.service import Service


def current_timestamp_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_seo_by_path(db: Session, page_path: str) -> PageSEO | None:
    return db.scalar(select(PageSEO).where(PageSEO.page_path == page_path))


def build_metadata(
    *,
    request: Request,
    db: Session,
    page_title: str,
    page_path: str,
    fallback_description: str,
    seo: PageSEO | None = None,
) -> dict[str, str]:
    seo = seo or load_seo_by_path(db, page_path)
    canonical_url = (
        seo.canonical_url
        if seo and seo.canonical_url
        else f"https://{request.app.state.settings.domain}{page_path}"
    )
    return {
        "page_title": seo.meta_title if seo and seo.meta_title else page_title,
        "meta_description": seo.meta_description if seo and seo.meta_description else fallback_description,
        "meta_keywords": seo.meta_keywords if seo and seo.meta_keywords else "",
        "canonical_url": canonical_url,
        "robots": seo.robots if seo and seo.robots else "index,follow",
        "og_title": seo.og_title if seo and seo.og_title else page_title,
        "og_description": seo.og_description if seo and seo.og_description else fallback_description,
        "og_image": seo.og_image if seo and seo.og_image else "",
        "twitter_title": seo.twitter_title if seo and seo.twitter_title else page_title,
        "twitter_description": seo.twitter_description if seo and seo.twitter_description else fallback_description,
        "twitter_image": seo.twitter_image if seo and seo.twitter_image else "",
        "schema_json": seo.schema_json if seo and seo.schema_json else "",
    }


def build_sitemap_entries(db: Session, domain: str) -> list[dict[str, str]]:
    entries: list[dict[str, str]] = [
        {"loc": f"https://{domain}/", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/about", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/services", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/products", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/industries", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/case-studies", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/blog", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/contact", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/book-consultation", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/privacy-policy", "lastmod": current_timestamp_iso()},
        {"loc": f"https://{domain}/terms-and-conditions", "lastmod": current_timestamp_iso()},
    ]

    for service in db.scalars(select(Service).where(Service.is_active.is_(True))):
        entries.append(
            {
                "loc": f"https://{domain}/services/{service.slug}",
                "lastmod": service.updated_at.replace(microsecond=0).isoformat(),
            }
        )

    for product in db.scalars(select(Product).where(Product.status == "published")):
        entries.append(
            {
                "loc": f"https://{domain}/products/{product.slug}",
                "lastmod": product.updated_at.replace(microsecond=0).isoformat(),
            }
        )

    for post in db.scalars(select(BlogPost).where(BlogPost.status == "published")):
        lastmod = post.updated_at or post.created_at
        entries.append(
            {
                "loc": f"https://{domain}/blog/{post.slug}",
                "lastmod": lastmod.replace(microsecond=0).isoformat(),
            }
        )

    for case_study in db.scalars(select(CaseStudy).where(CaseStudy.status == "published")):
        entries.append(
            {
                "loc": f"https://{domain}/case-studies/{case_study.slug}",
                "lastmod": case_study.updated_at.replace(microsecond=0).isoformat(),
            }
        )

    return entries


def render_robots_txt(domain: str) -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /admin/\n"
        f"Sitemap: https://{domain}/sitemap.xml\n"
    )
