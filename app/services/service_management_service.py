from __future__ import annotations

from sqlalchemy import select

from app.models.service import Service
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.services.base import BaseService, ConflictError, NotFoundError


class ServiceManagementService(BaseService):
    def create_service(self, payload: ServiceCreate) -> Service:
        existing = self.db.scalar(select(Service).where(Service.slug == payload.slug))
        if existing:
            raise ConflictError("A service with this slug already exists.")
        service = Service(**payload.model_dump())
        return self.add_and_commit(service)

    def get_service(self, service_id: int) -> Service:
        service = self.db.get(Service, service_id)
        if not service:
            raise NotFoundError("Service not found.")
        return service

    def get_service_by_slug(self, slug: str) -> Service:
        service = self.db.scalar(select(Service).where(Service.slug == slug))
        if not service:
            raise NotFoundError("Service not found.")
        return service

    def list_services(self, *, active_only: bool = False) -> list[Service]:
        statement = select(Service).order_by(Service.display_order.asc(), Service.created_at.desc())
        if active_only:
            statement = statement.where(Service.is_active.is_(True))
        return list(self.db.scalars(statement))

    def update_service(self, service_id: int, payload: ServiceUpdate) -> Service:
        service = self.get_service(service_id)
        updates = payload.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != service.slug:
            existing = self.db.scalar(select(Service).where(Service.slug == updates["slug"]))
            if existing:
                raise ConflictError("A service with this slug already exists.")
        for field, value in updates.items():
            setattr(service, field, value)
        self.commit()
        self.db.refresh(service)
        return service

    def delete_service(self, service_id: int) -> None:
        service = self.get_service(service_id)
        self.delete_and_commit(service)
