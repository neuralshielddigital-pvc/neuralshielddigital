from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.lead import Lead


class LeadRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_recent(self, limit: int = 10) -> list[Lead]:
        statement = select(Lead).order_by(Lead.created_at.desc()).limit(limit)
        return list(self.db.scalars(statement))
