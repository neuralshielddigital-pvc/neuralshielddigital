from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.case_study import CaseStudy


class CaseStudyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_published(self) -> list[CaseStudy]:
        statement = select(CaseStudy).where(CaseStudy.status == "published")
        return list(self.db.scalars(statement))
