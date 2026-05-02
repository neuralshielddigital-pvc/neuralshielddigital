from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.consultation_booking import ConsultationBooking
from app.models.lead import Lead


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    def get_summary(self) -> dict[str, int]:
        total_leads = self.db.scalar(select(func.count()).select_from(Lead)) or 0
        total_bookings = self.db.scalar(select(func.count()).select_from(ConsultationBooking)) or 0
        return {"total_leads": total_leads, "total_bookings": total_bookings}
