from __future__ import annotations

from sqlalchemy import select

from app.models.admin_user import AdminUser
from app.schemas.auth import AdminLoginRequest
from app.services.base import AuthenticationServiceError, BaseService, ConflictError, NotFoundError
from app.core.security import hash_password, verify_password


class AdminAuthenticationService(BaseService):
    def authenticate(self, payload: AdminLoginRequest | str, password: str | None = None) -> AdminUser:
        if isinstance(payload, AdminLoginRequest):
            email = str(payload.email)
            plain_password = payload.password
        else:
            email = payload
            if password is None:
                raise AuthenticationServiceError("Password is required.")
            plain_password = password

        admin = self.db.scalar(select(AdminUser).where(AdminUser.email == email))
        if not admin or not admin.is_active or not verify_password(plain_password, admin.password_hash):
            raise AuthenticationServiceError("Invalid email or password.")
        return admin

    def get_admin(self, admin_id: int) -> AdminUser:
        admin = self.db.get(AdminUser, admin_id)
        if not admin:
            raise NotFoundError("Admin user not found.")
        return admin

    def get_admin_by_email(self, email: str) -> AdminUser:
        admin = self.db.scalar(select(AdminUser).where(AdminUser.email == email))
        if not admin:
            raise NotFoundError("Admin user not found.")
        return admin

    def list_admins(self, *, active_only: bool = False) -> list[AdminUser]:
        statement = select(AdminUser).order_by(AdminUser.created_at.desc())
        if active_only:
            statement = statement.where(AdminUser.is_active.is_(True))
        return list(self.db.scalars(statement))

    def create_admin(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
        role: str = "editor",
        is_active: bool = True,
    ) -> AdminUser:
        existing = self.db.scalar(select(AdminUser).where(AdminUser.email == email))
        if existing:
            raise ConflictError("An admin with this email already exists.")

        admin = AdminUser(
            email=email,
            full_name=full_name,
            password_hash=hash_password(password),
            role=role,
            is_active=is_active,
        )
        return self.add_and_commit(admin)

    def update_password(self, admin_id: int, new_password: str) -> AdminUser:
        admin = self.get_admin(admin_id)
        admin.password_hash = hash_password(new_password)
        self.commit()
        self.db.refresh(admin)
        return admin

    def set_active_status(self, admin_id: int, is_active: bool) -> AdminUser:
        admin = self.get_admin(admin_id)
        admin.is_active = is_active
        self.commit()
        self.db.refresh(admin)
        return admin


AuthService = AdminAuthenticationService
