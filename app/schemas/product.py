from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(..., min_length=2, max_length=255)
    slug: str = Field(..., min_length=2, max_length=255)
    tagline: str | None = Field(default=None, max_length=255)
    short_description: str = Field(..., min_length=10, max_length=500)
    full_description: str = Field(..., min_length=20)
    product_type: str = Field(default="platform", min_length=2, max_length=100)
    status: str = Field(default="draft", max_length=50)
    website_url: str | None = Field(default=None, max_length=500)
    cta_label: str | None = Field(default=None, max_length=100)
    cta_url: str | None = Field(default=None, max_length=255)
    pricing_summary: str | None = Field(default=None, max_length=255)
    display_order: int = Field(default=0, ge=0)
    is_featured: bool = False
    published_at: datetime | None = None

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if " " in cleaned:
            raise ValueError("Slug must not contain spaces.")
        return cleaned


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=2, max_length=255)
    slug: str | None = Field(default=None, min_length=2, max_length=255)
    tagline: str | None = Field(default=None, max_length=255)
    short_description: str | None = Field(default=None, min_length=10, max_length=500)
    full_description: str | None = Field(default=None, min_length=20)
    product_type: str | None = Field(default=None, min_length=2, max_length=100)
    status: str | None = Field(default=None, max_length=50)
    website_url: str | None = Field(default=None, max_length=500)
    cta_label: str | None = Field(default=None, max_length=100)
    cta_url: str | None = Field(default=None, max_length=255)
    pricing_summary: str | None = Field(default=None, max_length=255)
    display_order: int | None = Field(default=None, ge=0)
    is_featured: bool | None = None
    published_at: datetime | None = None


class ProductRead(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
