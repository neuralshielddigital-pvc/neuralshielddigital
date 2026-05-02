from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost
from app.models.case_study import CaseStudy
from app.models.page_seo import PageSEO
from app.models.product import Product
from app.models.service import Service
from app.models.testimonial import Testimonial
from app.routers.deps import get_database
from app.services.product_management_service import ProductManagementService
from app.services.service_management_service import ServiceManagementService
from app.utils.seo import build_metadata, render_robots_txt


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(tags=["public-pages"])

def _render(
    request: Request,
    template_name: str,
    *,
    db: Session,
    page_title: str,
    page_path: str,
    fallback_description: str,
    context: dict | None = None,
    seo: PageSEO | None = None,
    status_code: int = status.HTTP_200_OK,
):
    payload = {
        "request": request,
        **build_metadata(
            request=request,
            db=db,
            page_title=page_title,
            page_path=page_path,
            fallback_description=fallback_description,
            seo=seo,
        ),
    }
    if context:
        payload.update(context)
    return templates.TemplateResponse(template_name, payload, status_code=status_code)


@router.get("/", response_class=HTMLResponse, name="home")
def home(request: Request, db: Session = Depends(get_database)):
    services = ServiceManagementService(db).list_services(active_only=True)[:6]
    products = ProductManagementService(db).list_products(published_only=True)[:4]
    testimonials = list(
        db.scalars(
            select(Testimonial)
            .where(Testimonial.is_active.is_(True), Testimonial.is_featured.is_(True))
            .order_by(Testimonial.display_order.asc(), Testimonial.created_at.desc())
            .limit(6)
        )
    )
    posts = list(
        db.scalars(
            select(BlogPost)
            .where(BlogPost.status == "published")
            .order_by(BlogPost.published_at.desc().nullslast(), BlogPost.created_at.desc())
            .limit(3)
        )
    )
    return _render(
        request,
        "public/home.html",
        db=db,
        page_title="NeuralShield Digital",
        page_path="/",
        fallback_description="AI engineering, automation, machine learning, and enterprise software delivery for modern businesses.",
        context={
            "services": services,
            "products": products,
            "testimonials": testimonials,
            "recent_posts": posts,
        },
    )


@router.get("/about", response_class=HTMLResponse, name="about")
def about(request: Request, db: Session = Depends(get_database)):
    featured_services = ServiceManagementService(db).list_services(active_only=True)[:4]
    return _render(
        request,
        "public/about.html",
        db=db,
        page_title="About",
        page_path="/about",
        fallback_description="Learn about NeuralShield Digital, our AI capabilities, delivery approach, and mission.",
        context={"featured_services": featured_services},
    )


@router.get("/services", response_class=HTMLResponse, name="services-list")
def services_listing(request: Request, db: Session = Depends(get_database)):
    services = ServiceManagementService(db).list_services(active_only=True)
    return _render(
        request,
        "public/services.html",
        db=db,
        page_title="Services",
        page_path="/services",
        fallback_description="Explore AI consulting, agentic AI, machine learning, NLP, MLOps, automation, and custom software services.",
        context={"services": services},
    )


@router.get("/services/{slug}", response_class=HTMLResponse, name="service-detail")
def service_detail(slug: str, request: Request, db: Session = Depends(get_database)):
    service = ServiceManagementService(db).get_service_by_slug(slug)
    seo = db.scalar(select(PageSEO).where(PageSEO.page_type == "service", PageSEO.object_id == service.id))
    related_services = list(
        db.scalars(
            select(Service)
            .where(Service.is_active.is_(True), Service.id != service.id)
            .order_by(Service.display_order.asc(), Service.created_at.desc())
            .limit(3)
        )
    )
    return _render(
        request,
        "public/service_detail.html",
        db=db,
        page_title=service.name,
        page_path=f"/services/{service.slug}",
        fallback_description=service.short_description,
        context={"service": service, "related_services": related_services, "slug": slug},
        seo=seo,
    )


@router.get("/products", response_class=HTMLResponse, name="products-list")
def products_listing(request: Request, db: Session = Depends(get_database)):
    products = ProductManagementService(db).list_products(published_only=True)
    return _render(
        request,
        "public/products.html",
        db=db,
        page_title="Products",
        page_path="/products",
        fallback_description="Discover AI products, automation tools, and digital platforms built by NeuralShield Digital.",
        context={"products": products},
    )


@router.get("/products/{slug}", response_class=HTMLResponse, name="product-detail")
def product_detail(slug: str, request: Request, db: Session = Depends(get_database)):
    product = ProductManagementService(db).get_product_by_slug(slug)
    seo = db.scalar(select(PageSEO).where(PageSEO.page_type == "product", PageSEO.object_id == product.id))
    related_products = list(
        db.scalars(
            select(Product)
            .where(Product.status == "published", Product.id != product.id)
            .order_by(Product.display_order.asc(), Product.created_at.desc())
            .limit(3)
        )
    )
    return _render(
        request,
        "public/product_detail.html",
        db=db,
        page_title=product.name,
        page_path=f"/products/{product.slug}",
        fallback_description=product.short_description,
        context={"product": product, "related_products": related_products, "slug": slug},
        seo=seo,
    )


@router.get("/industries", response_class=HTMLResponse, name="industries")
def industries(request: Request, db: Session = Depends(get_database)):
    featured_services = ServiceManagementService(db).list_services(active_only=True)[:6]
    return _render(
        request,
        "public/industries.html",
        db=db,
        page_title="Industries",
        page_path="/industries",
        fallback_description="Industry-tailored AI and software delivery for enterprise, operations, data, and automation use cases.",
        context={"featured_services": featured_services},
    )


@router.get("/case-studies", response_class=HTMLResponse, name="case-studies")
def case_studies_listing(request: Request, db: Session = Depends(get_database)):
    case_studies = list(
        db.scalars(
            select(CaseStudy)
            .where(CaseStudy.status == "published")
            .order_by(CaseStudy.published_at.desc().nullslast(), CaseStudy.created_at.desc())
        )
    )
    return _render(
        request,
        "public/case_studies.html",
        db=db,
        page_title="Case Studies",
        page_path="/case-studies",
        fallback_description="See how NeuralShield Digital delivers measurable outcomes through AI systems, automation, and engineering.",
        context={"case_studies": case_studies},
    )


@router.get("/case-studies/{slug}", response_class=HTMLResponse, name="case-study-detail")
def case_study_detail(slug: str, request: Request, db: Session = Depends(get_database)):
    case_study = db.scalar(select(CaseStudy).where(CaseStudy.slug == slug, CaseStudy.status == "published"))
    if not case_study:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Case study not found.")
    related_case_studies = list(
        db.scalars(
            select(CaseStudy)
            .where(CaseStudy.status == "published", CaseStudy.id != case_study.id)
            .order_by(CaseStudy.published_at.desc().nullslast(), CaseStudy.created_at.desc())
            .limit(3)
        )
    )
    seo = db.scalar(select(PageSEO).where(PageSEO.page_type == "case_study", PageSEO.object_id == case_study.id))
    return _render(
        request,
        "public/case_study_detail.html",
        db=db,
        page_title=case_study.seo_title or case_study.title,
        page_path=f"/case-studies/{case_study.slug}",
        fallback_description=case_study.seo_description or case_study.challenge[:200],
        context={"case_study": case_study, "related_case_studies": related_case_studies, "slug": slug},
        seo=seo,
    )


@router.get("/contact", response_class=HTMLResponse, name="contact")
def contact_page(
    request: Request,
    submitted: int = Query(default=0, ge=0, le=1),
    db: Session = Depends(get_database),
):
    return _render(
        request,
        "public/contact.html",
        db=db,
        page_title="Contact",
        page_path="/contact",
        fallback_description="Contact NeuralShield Digital to discuss AI consulting, product builds, automation, and custom software solutions.",
        context={
            "form_data": {
                "full_name": "",
                "email": "",
                "phone": "",
                "company_name": "",
                "subject": "",
                "message": "",
                "service_interest": "",
                "source_page": "/contact",
            },
            "form_errors": {},
            "form_success": bool(submitted),
        },
    )


@router.get("/book-consultation", response_class=HTMLResponse, name="book-consultation")
def book_consultation_page(
    request: Request,
    submitted: int = Query(default=0, ge=0, le=1),
    db: Session = Depends(get_database),
):
    return _render(
        request,
        "public/consultation.html",
        db=db,
        page_title="Book Consultation",
        page_path="/book-consultation",
        fallback_description="Book an AI strategy or technical consultation with NeuralShield Digital.",
        context={
            "form_data": {
                "full_name": "",
                "email": "",
                "phone": "",
                "company_name": "",
                "consultation_type": "strategy",
                "preferred_datetime": "",
                "timezone": "Asia/Calcutta",
                "project_details": "",
            },
            "form_errors": {},
            "form_success": bool(submitted),
        },
    )


@router.get("/privacy-policy", response_class=HTMLResponse, name="privacy-policy")
def privacy_policy(request: Request, db: Session = Depends(get_database)):
    return _render(
        request,
        "public/privacy_policy.html",
        db=db,
        page_title="Privacy Policy",
        page_path="/privacy-policy",
        fallback_description="Read the NeuralShield Digital privacy policy.",
    )


@router.get("/terms-and-conditions", response_class=HTMLResponse, name="terms-and-conditions")
def terms_and_conditions(request: Request, db: Session = Depends(get_database)):
    return _render(
        request,
        "public/terms_and_conditions.html",
        db=db,
        page_title="Terms and Conditions",
        page_path="/terms-and-conditions",
        fallback_description="Read the NeuralShield Digital terms and conditions.",
    )


@router.get("/health", response_class=PlainTextResponse, name="health")
def healthcheck() -> str:
    return "ok"


@router.get("/robots.txt", response_class=PlainTextResponse, name="robots")
def robots(request: Request) -> str:
    domain = request.app.state.settings.domain
    return render_robots_txt(domain)
