from __future__ import annotations

from sqlalchemy import select

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.services.base import BaseService, ConflictError, NotFoundError


class ProductManagementService(BaseService):
    def create_product(self, payload: ProductCreate) -> Product:
        existing = self.db.scalar(select(Product).where(Product.slug == payload.slug))
        if existing:
            raise ConflictError("A product with this slug already exists.")
        product = Product(**payload.model_dump())
        return self.add_and_commit(product)

    def get_product(self, product_id: int) -> Product:
        product = self.db.get(Product, product_id)
        if not product:
            raise NotFoundError("Product not found.")
        return product

    def get_product_by_slug(self, slug: str) -> Product:
        product = self.db.scalar(select(Product).where(Product.slug == slug))
        if not product:
            raise NotFoundError("Product not found.")
        return product

    def list_products(self, *, published_only: bool = False) -> list[Product]:
        statement = select(Product).order_by(Product.display_order.asc(), Product.created_at.desc())
        if published_only:
            statement = statement.where(Product.status == "published")
        return list(self.db.scalars(statement))

    def update_product(self, product_id: int, payload: ProductUpdate) -> Product:
        product = self.get_product(product_id)
        updates = payload.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != product.slug:
            existing = self.db.scalar(select(Product).where(Product.slug == updates["slug"]))
            if existing:
                raise ConflictError("A product with this slug already exists.")
        for field, value in updates.items():
            setattr(product, field, value)
        self.commit()
        self.db.refresh(product)
        return product

    def delete_product(self, product_id: int) -> None:
        product = self.get_product(product_id)
        self.delete_and_commit(product)
