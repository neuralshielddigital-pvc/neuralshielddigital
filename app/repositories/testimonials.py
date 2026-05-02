from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.testimonial import Testimonial


class TestimonialRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_featured(self) -> list[Testimonial]:
        statement = select(Testimonial).where(Testimonial.is_featured.is_(True)).order_by(Testimonial.display_order.asc())
        return list(self.db.scalars(statement))
