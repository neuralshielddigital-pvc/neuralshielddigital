from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PageSEOBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    page_key: str = Field(..., min_length=2, max_length=100)
    page_type: str = Field(..., min_length=2, max_length=50)
    object_id: int | None = None
    page_path: str = Field(..., min_length=1, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)
    meta_keywords: str | None = Field(default=None, max_length=500)
    canonical_url: str | None = Field(default=None, max_length=500)
    robots: str = Field(default="index,follow", max_length=100)
    og_title: str | None = Field(default=None, max_length=255)
    og_description: str | None = Field(default=None, max_length=500)
    og_image: str | None = Field(default=None, max_length=500)
    twitter_title: str | None = Field(default=None, max_length=255)
    twitter_description: str | None = Field(default=None, max_length=500)
    twitter_image: str | None = Field(default=None, max_length=500)
    schema_json: str | None = None

    @field_validator("page_path")
    @classmethod
    def validate_page_path(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned.startswith("/"):
            raise ValueError("page_path must start with '/'.")
        return cleaned


class PageSEOCreate(PageSEOBase):
    pass


class PageSEOUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    page_key: str | None = Field(default=None, min_length=2, max_length=100)
    page_type: str | None = Field(default=None, min_length=2, max_length=50)
    object_id: int | None = None
    page_path: str | None = Field(default=None, min_length=1, max_length=255)
    meta_title: str | None = Field(default=None, max_length=255)
    meta_description: str | None = Field(default=None, max_length=500)
    meta_keywords: str | None = Field(default=None, max_length=500)
    canonical_url: str | None = Field(default=None, max_length=500)
    robots: str | None = Field(default=None, max_length=100)
    og_title: str | None = Field(default=None, max_length=255)
    og_description: str | None = Field(default=None, max_length=500)
    og_image: str | None = Field(default=None, max_length=500)
    twitter_title: str | None = Field(default=None, max_length=255)
    twitter_description: str | None = Field(default=None, max_length=500)
    twitter_image: str | None = Field(default=None, max_length=500)
    schema_json: str | None = None


class PageSEORead(PageSEOBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
