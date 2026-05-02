from __future__ import annotations
from fastapi.responses import RedirectResponse
import os
from contextlib import asynccontextmanager
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.core.config import Settings, get_settings
from app.core.database import close_engine, ping_database
from app.core.logging import configure_logging, get_logger
from app.core.middleware import register_middleware
from app.routers import (
    admin_auth,
    admin_blog,
    admin_blog_categories,
    admin_bookings,
    admin_dashboard,
    admin_leads,
    admin_products,
    admin_seo,
    admin_services,
    admin_testimonials,
    blog,
    public_forms,
    public_pages,
)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


def create_application(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings)
    logger = get_logger("app.startup")
    
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        logger.info(
            "Application startup",
            extra={
                "environment": settings.environment,
                "debug": settings.debug,
                "domain": settings.domain,
            },
        )
        ping_database()
        yield
        close_engine()
        logger.info("Application shutdown complete")

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        # lifespan=lifespan,
        
    )

    app.state.settings = settings
    app.state.templates = templates

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        same_site="lax",
        https_only=False,
    )
    @app.middleware("http")
    async def admin_auth_guard(request: Request, call_next):
        path = request.url.path

        if path.startswith("/admin") and path != "/admin/login":
            admin = request.session.get("admin")

            if not admin:
                return RedirectResponse(url="/admin/login", status_code=302)

        return await call_next(request)
    app.mount("/static", StaticFiles(directory="app/static"), name="static")
    register_routes(app)


    return app

    

    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    register_middleware(app)
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key,
        same_site="lax",
        https_only=False,
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
    

    @app.get("/test-logo")
    def test_logo():
        return {"path": str(STATIC_DIR)}

    templates.env.globals["settings"] = settings

    register_exception_handlers(app)
    register_routes(app)

    return app


def register_routes(app: FastAPI) -> None:
    app.add_middleware(
        SessionMiddleware,
        secret_key=app.state.settings.secret_key,
        same_site="lax",
        https_only=False,
    )
    app.include_router(public_pages.router)
    app.include_router(public_forms.router)
    app.include_router(blog.router)
    app.include_router(admin_auth.router)
    app.include_router(admin_dashboard.router)
    app.include_router(admin_leads.router)
    app.include_router(admin_bookings.router)
    app.include_router(admin_services.router)
    app.include_router(admin_products.router)
    app.include_router(admin_blog.router)
    app.include_router(admin_blog_categories.router)
    app.include_router(admin_testimonials.router)
    app.include_router(admin_seo.router)

    @app.get("/health/live", response_class=PlainTextResponse, tags=["health"])
    def live_check() -> str:
        return "alive"

    @app.get("/health/ready", response_class=JSONResponse, tags=["health"])
    def readiness_check() -> JSONResponse:
        ping_database()
        return JSONResponse({"status": "ready"})


def register_exception_handlers(app: FastAPI) -> None:
    logger = get_logger("app.errors")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.warning(
            "HTTP exception",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "status_code": exc.status_code,
                "detail": exc.detail,
            },
        )
        if exc.status_code == status.HTTP_404_NOT_FOUND:
            return templates.TemplateResponse(
                "public/404.html",
                {
                    "request": request,
                    "page_title": "Page Not Found",
                    "meta_description": "The page you requested could not be found.",
                    "meta_keywords": "",
                    "canonical_url": f"https://{request.app.state.settings.domain}{request.url.path}",
                    "robots": "noindex,follow",
                    "og_title": "Page Not Found",
                    "og_description": "The page you requested could not be found.",
                    "og_image": "",
                    "twitter_title": "Page Not Found",
                    "twitter_description": "The page you requested could not be found.",
                    "twitter_image": "",
                    "schema_json": "",
                },
                status_code=status.HTTP_404_NOT_FOUND,
            )
        return JSONResponse(
            {"detail": exc.detail},
            status_code=exc.status_code,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.warning(
            "Validation error",
            extra={
                "path": str(request.url.path),
                "method": request.method,
                "errors": exc.errors(),
            },
        )
        return JSONResponse(
            {"detail": "Invalid request.", "errors": exc.errors()},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception(
            "Unhandled server error",
            extra={"path": str(request.url.path), "method": request.method},
        )
        if request.url.path.startswith("/admin") or request.url.path.startswith("/api"):
            return JSONResponse(
                {"detail": "Internal server error."},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return templates.TemplateResponse(
            "public/500.html",
            {
                "request": request,
                "page_title": "Server Error",
                "meta_description": "An unexpected error occurred while loading this page.",
                "meta_keywords": "",
                "canonical_url": f"https://{request.app.state.settings.domain}{request.url.path}",
                "robots": "noindex,follow",
                "og_title": "Server Error",
                "og_description": "An unexpected error occurred while loading this page.",
                "og_image": "",
                "twitter_title": "Server Error",
                "twitter_description": "An unexpected error occurred while loading this page.",
                "twitter_image": "",
                "schema_json": "",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    register_middleware(app)
    register_routes(app)

    return app

app = create_application()
