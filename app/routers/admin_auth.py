from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.forms.admin_auth import AdminLoginForm
from app.routers.deps import get_database
from app.schemas.auth import AdminLoginRequest
from app.services.auth_service import AdminAuthenticationService
from app.services.base import AuthenticationServiceError


templates = Jinja2Templates(directory=str(Path("app/templates")))
router = APIRouter(prefix="/admin", tags=["admin-auth"])


@router.get("/login", name="admin-login")
async def admin_login_page(request: Request):
    return templates.TemplateResponse(
        "admin/login.html",
        {
            "request": request,
            "page_title": "Admin Login",
            "form_data": {"email": ""},
            "form_errors": {},
            "auth_error": None,
        },
    )    


@router.post("/login", name="admin-login-submit")
def admin_login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_database),
):
    form_input = {"email": email, "password": password}
    validation = AdminLoginForm.validate(form_input)
    if not validation.is_valid:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "page_title": "Admin Login",
                "form_data": {"email": email},
                "form_errors": validation.errors,
                "auth_error": None,
            },
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        payload = AdminLoginRequest(**validation.cleaned_data)
        admin = AdminAuthenticationService(db).authenticate(payload)
    except AuthenticationServiceError as exc:
        return templates.TemplateResponse(
            "admin/login.html",
            {
                "request": request,
                "page_title": "Admin Login",
                "form_data": {"email": email},
                "form_errors": {},
                "auth_error": str(exc),
            },
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    request.session["admin"] = {
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
        "role": admin.role,
    }
    return RedirectResponse("/admin/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/logout", name="admin-logout")
def admin_logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=status.HTTP_303_SEE_OTHER)
