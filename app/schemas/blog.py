from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BlogCategoryBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if " " in cleaned:
            raise ValueError("Slug must not contain spaces.")
        return cleaned


class BlogCategoryCreate(BlogCategoryBase):
    pass


class BlogCategoryUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class BlogCategoryRead(BlogCategoryBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class BlogPostBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: int | None = None
    author_id: int | None = None
    title: str = Field(..., min_length=5, max_length=255)
    slug: str = Field(..., min_length=5, max_length=255)
    excerpt: str | None = Field(default=None, max_length=500)
    featured_image: str | None = Field(default=None, max_length=500)
    content_markdown: str = Field(..., min_length=20)
    content_html: str | None = None
    status: str = Field(default="draft", max_length=50)
    is_featured: bool = False
    published_at: datetime | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if " " in cleaned:
            raise ValueError("Slug must not contain spaces.")
        return cleaned


class BlogPostCreate(BlogPostBase):
    pass


class BlogPostUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    category_id: int | None = None
    author_id: int | None = None
    title: str | None = Field(default=None, min_length=5, max_length=255)
    slug: str | None = Field(default=None, min_length=5, max_length=255)
    excerpt: str | None = Field(default=None, max_length=500)
    featured_image: str | None = Field(default=None, max_length=500)
    content_markdown: str | None = Field(default=None, min_length=20)
    content_html: str | None = None
    status: str | None = Field(default=None, max_length=50)
    is_featured: bool | None = None
    published_at: datetime | None = None


class BlogPostRead(BlogPostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    category: BlogCategoryRead | None = None
