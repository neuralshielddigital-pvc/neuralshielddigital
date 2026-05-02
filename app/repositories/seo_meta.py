from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.seo_page_meta import SeoPageMeta


class SeoRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_page_key(self, page_key: str) -> SeoPageMeta | None:
        return self.db.scalar(select(SeoPageMeta).where(SeoPageMeta.page_key == page_key))
