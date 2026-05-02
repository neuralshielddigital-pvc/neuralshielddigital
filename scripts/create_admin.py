from __future__ import annotations

import argparse
import re

from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.models.admin_user import AdminUser
from app.services.auth_service import AdminAuthenticationService
from app.services.base import ConflictError


PASSWORD_COMPLEXITY_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


def build_parser() -> argparse.ArgumentParser:
    settings = get_settings()
    parser = argparse.ArgumentParser(description="Create the first NeuralShield Digital admin user.")
    parser.add_argument("--email", default=str(settings.admin_default_email), help="Admin email address.")
    parser.add_argument("--name", default="NeuralShield Digital Admin", help="Admin full name.")
    parser.add_argument("--password", default=settings.admin_default_password, help="Admin password.")
    parser.add_argument("--role", default="super_admin", help="Admin role.")
    return parser


def validate_password(password: str) -> None:
    if not PASSWORD_COMPLEXITY_RE.match(password):
        raise ValueError("Password must be at least 8 characters and include both letters and numbers.")


def main() -> None:
    args = build_parser().parse_args()
    validate_password(args.password)
    session = SessionLocal()
    try:
        existing = session.scalar(select(AdminUser).where(AdminUser.email == args.email))
        if existing:
            print(f"Admin user already exists: {existing.email}")
            return

        admin = AdminAuthenticationService(session).create_admin(
            email=args.email,
            full_name=args.name,
            password=args.password,
            role=args.role,
            is_active=True,
        )
        print(f"Created admin user: {admin.email} ({admin.role})")
        print("You can now sign in at /admin/login.")
    except ConflictError as exc:
        print(str(exc))
    except ValueError as exc:
        print(str(exc))
    finally:
        session.close()


if __name__ == "__main__":
    main()
