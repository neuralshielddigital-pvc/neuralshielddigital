from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.service import Service


class ServiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_active(self) -> list[Service]:
        statement = select(Service).where(Service.is_active.is_(True)).order_by(Service.display_order.asc())
        return list(self.db.scalars(statement))
