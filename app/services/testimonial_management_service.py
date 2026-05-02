from __future__ import annotations

from sqlalchemy import select

from app.models.testimonial import Testimonial
from app.schemas.testimonial import TestimonialCreate, TestimonialUpdate
from app.services.base import BaseService, NotFoundError


class TestimonialManagementService(BaseService):
    def create_testimonial(self, payload: TestimonialCreate) -> Testimonial:
        testimonial = Testimonial(**payload.model_dump())
        return self.add_and_commit(testimonial)

    def get_testimonial(self, testimonial_id: int) -> Testimonial:
        testimonial = self.db.get(Testimonial, testimonial_id)
        if not testimonial:
            raise NotFoundError("Testimonial not found.")
        return testimonial

    def list_testimonials(self, *, active_only: bool = False, featured_only: bool = False) -> list[Testimonial]:
        statement = select(Testimonial).order_by(Testimonial.display_order.asc(), Testimonial.created_at.desc())
        if active_only:
            statement = statement.where(Testimonial.is_active.is_(True))
        if featured_only:
            statement = statement.where(Testimonial.is_featured.is_(True))
        return list(self.db.scalars(statement))

    def update_testimonial(self, testimonial_id: int, payload: TestimonialUpdate) -> Testimonial:
        testimonial = self.get_testimonial(testimonial_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(testimonial, field, value)
        self.commit()
        self.db.refresh(testimonial)
        return testimonial

    def delete_testimonial(self, testimonial_id: int) -> None:
        testimonial = self.get_testimonial(testimonial_id)
        self.delete_and_commit(testimonial)
