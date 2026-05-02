from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.consultation_booking import ConsultationBooking


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_recent(self, limit: int = 10) -> list[ConsultationBooking]:
        statement = select(ConsultationBooking).order_by(ConsultationBooking.created_at.desc()).limit(limit)
        return list(self.db.scalars(statement))
