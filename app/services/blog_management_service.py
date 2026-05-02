from __future__ import annotations

from sqlalchemy import select

from app.models.blog_category import BlogCategory
from app.models.blog_post import BlogPost
from app.schemas.blog import (
    BlogCategoryCreate,
    BlogCategoryUpdate,
    BlogPostCreate,
    BlogPostUpdate,
)
from app.services.base import BaseService, ConflictError, NotFoundError


class BlogManagementService(BaseService):
    def create_category(self, payload: BlogCategoryCreate) -> BlogCategory:
        existing = self.db.scalar(select(BlogCategory).where(BlogCategory.slug == payload.slug))
        if existing:
            raise ConflictError("A blog category with this slug already exists.")
        category = BlogCategory(**payload.model_dump())
        return self.add_and_commit(category)

    def update_category(self, category_id: int, payload: BlogCategoryUpdate) -> BlogCategory:
        category = self.get_category(category_id)
        updates = payload.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != category.slug:
            existing = self.db.scalar(select(BlogCategory).where(BlogCategory.slug == updates["slug"]))
            if existing:
                raise ConflictError("A blog category with this slug already exists.")
        for field, value in updates.items():
            setattr(category, field, value)
        self.commit()
        self.db.refresh(category)
        return category

    def get_category(self, category_id: int) -> BlogCategory:
        category = self.db.get(BlogCategory, category_id)
        if not category:
            raise NotFoundError("Blog category not found.")
        return category

    def list_categories(self) -> list[BlogCategory]:
        return list(self.db.scalars(select(BlogCategory).order_by(BlogCategory.name.asc())))

    def create_post(self, payload: BlogPostCreate) -> BlogPost:
        existing = self.db.scalar(select(BlogPost).where(BlogPost.slug == payload.slug))
        if existing:
            raise ConflictError("A blog post with this slug already exists.")
        post = BlogPost(**payload.model_dump())
        return self.add_and_commit(post)

    def update_post(self, post_id: int, payload: BlogPostUpdate) -> BlogPost:
        post = self.get_post(post_id)
        updates = payload.model_dump(exclude_unset=True)
        if "slug" in updates and updates["slug"] != post.slug:
            existing = self.db.scalar(select(BlogPost).where(BlogPost.slug == updates["slug"]))
            if existing:
                raise ConflictError("A blog post with this slug already exists.")
        for field, value in updates.items():
            setattr(post, field, value)
        self.commit()
        self.db.refresh(post)
        return post

    def get_post(self, post_id: int) -> BlogPost:
        post = self.db.get(BlogPost, post_id)
        if not post:
            raise NotFoundError("Blog post not found.")
        return post

    def get_post_by_slug(self, slug: str) -> BlogPost:
        post = self.db.scalar(select(BlogPost).where(BlogPost.slug == slug))
        if not post:
            raise NotFoundError("Blog post not found.")
        return post

    def list_posts(self, *, published_only: bool = False) -> list[BlogPost]:
        statement = select(BlogPost).order_by(BlogPost.created_at.desc())
        if published_only:
            statement = statement.where(BlogPost.status == "published")
        return list(self.db.scalars(statement))

    def delete_post(self, post_id: int) -> None:
        post = self.get_post(post_id)
        self.delete_and_commit(post)
