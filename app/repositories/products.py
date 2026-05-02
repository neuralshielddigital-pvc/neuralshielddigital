from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_published(self) -> list[Product]:
        statement = select(Product).where(Product.status == "published").order_by(Product.display_order.asc())
        return list(self.db.scalars(statement))
