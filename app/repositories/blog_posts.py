from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.blog_post import BlogPost


class BlogPostRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_published(self) -> list[BlogPost]:
        statement = select(BlogPost).where(BlogPost.status == "published").order_by(BlogPost.published_at.desc())
        return list(self.db.scalars(statement))
