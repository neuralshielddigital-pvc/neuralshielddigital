from __future__ import annotations

from sqlalchemy import select

from app.models.page_seo import PageSEO
from app.schemas.seo import PageSEOCreate, PageSEOUpdate
from app.services.base import BaseService, ConflictError, NotFoundError


class SEOMetadataService(BaseService):
    def create_metadata(self, payload: PageSEOCreate) -> PageSEO:
        existing = self.db.scalar(select(PageSEO).where(PageSEO.page_key == payload.page_key))
        if existing:
            raise ConflictError("SEO metadata for this page key already exists.")
        page_seo = PageSEO(**payload.model_dump())
        return self.add_and_commit(page_seo)

    def get_metadata(self, seo_id: int) -> PageSEO:
        metadata = self.db.get(PageSEO, seo_id)
        if not metadata:
            raise NotFoundError("SEO metadata not found.")
        return metadata

    def get_by_page_key(self, page_key: str) -> PageSEO:
        metadata = self.db.scalar(select(PageSEO).where(PageSEO.page_key == page_key))
        if not metadata:
            raise NotFoundError("SEO metadata not found.")
        return metadata

    def get_by_path(self, page_path: str) -> PageSEO:
        metadata = self.db.scalar(select(PageSEO).where(PageSEO.page_path == page_path))
        if not metadata:
            raise NotFoundError("SEO metadata not found.")
        return metadata

    def list_metadata(self, *, page_type: str | None = None) -> list[PageSEO]:
        statement = select(PageSEO).order_by(PageSEO.created_at.desc())
        if page_type:
            statement = statement.where(PageSEO.page_type == page_type)
        return list(self.db.scalars(statement))

    def update_metadata(self, seo_id: int, payload: PageSEOUpdate) -> PageSEO:
        metadata = self.get_metadata(seo_id)
        updates = payload.model_dump(exclude_unset=True)
        if "page_key" in updates and updates["page_key"] != metadata.page_key:
            existing = self.db.scalar(select(PageSEO).where(PageSEO.page_key == updates["page_key"]))
            if existing:
                raise ConflictError("SEO metadata for this page key already exists.")
        for field, value in updates.items():
            setattr(metadata, field, value)
        self.commit()
        self.db.refresh(metadata)
        return metadata

    def delete_metadata(self, seo_id: int) -> None:
        metadata = self.get_metadata(seo_id)
        self.delete_and_commit(metadata)
