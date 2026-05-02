from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TestimonialBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    client_name: str = Field(..., min_length=2, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    designation: str | None = Field(default=None, max_length=255)
    testimonial_text: str = Field(..., min_length=10, max_length=5000)
    rating: int = Field(default=5, ge=1, le=5)
    is_featured: bool = False
    display_order: int = Field(default=0, ge=0)
    source_url: str | None = Field(default=None, max_length=500)
    is_active: bool = True


class TestimonialCreate(TestimonialBase):
    pass


class TestimonialUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    client_name: str | None = Field(default=None, min_length=2, max_length=255)
    company_name: str | None = Field(default=None, max_length=255)
    designation: str | None = Field(default=None, max_length=255)
    testimonial_text: str | None = Field(default=None, min_length=10, max_length=5000)
    rating: int | None = Field(default=None, ge=1, le=5)
    is_featured: bool | None = None
    display_order: int | None = Field(default=None, ge=0)
    source_url: str | None = Field(default=None, max_length=500)
    is_active: bool | None = None


class TestimonialRead(TestimonialBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
