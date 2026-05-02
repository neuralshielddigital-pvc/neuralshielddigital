from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _clean_optional_text(value: str | None, max_length: int) -> str:
    if value is None:
        return ""
    cleaned = " ".join(value.strip().split())
    return cleaned[:max_length]


class ContactSubmission(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Name of the person submitting the inquiry.",
    )
    email: EmailStr = Field(..., description="Primary email address for follow-up.")
    phone: str = Field(
        default="",
        max_length=50,
        description="Optional phone or WhatsApp number.",
    )
    company_name: str = Field(
        default="",
        max_length=255,
        description="Optional company or organization name.",
    )
    subject: str = Field(
        default="",
        max_length=255,
        description="Optional inquiry subject line.",
    )
    message: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Main inquiry body submitted through the contact form.",
    )
    service_interest: str = Field(
        default="",
        max_length=255,
        description="Optional service or capability the lead is interested in.",
    )
    source_page: str = Field(
        default="/contact",
        max_length=255,
        description="Public page path where the lead submitted the form.",
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return cleaned

    @field_validator("phone", "company_name", "subject", "service_interest", "source_page", mode="before")
    @classmethod
    def normalize_optional_fields(cls, value: str | None, info) -> str:
        max_lengths = {
            "phone": 50,
            "company_name": 255,
            "subject": 255,
            "service_interest": 255,
            "source_page": 255,
        }
        return _clean_optional_text(value, max_lengths[info.field_name])

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Message must contain at least 10 characters.")
        return cleaned

    @field_validator("source_page")
    @classmethod
    def validate_source_page(cls, value: str) -> str:
        if not value.startswith("/"):
            raise ValueError("source_page must start with '/'.")
        return value


class ContactSubmissionCreate(ContactSubmission):
    """Alias schema kept for service-layer clarity when creating new records."""


class ContactLeadUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company_name: str | None = Field(default=None, max_length=255)
    subject: str | None = Field(default=None, max_length=255)
    message: str | None = Field(default=None, min_length=10, max_length=5000)
    service_interest: str | None = Field(default=None, max_length=255)
    source_page: str | None = Field(default=None, max_length=255)
    lead_source: str | None = Field(default=None, max_length=100)
    status: str | None = Field(default=None, max_length=50)
    priority: str | None = Field(default=None, max_length=50)
    budget_range: str | None = Field(default=None, max_length=100)
    notes: str | None = Field(default=None, max_length=5000)
    assigned_admin_id: int | None = None


class ContactLeadResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: str
    company_name: str
    subject: str
    message: str
    service_interest: str
    source_page: str
    status: str
    lead_source: str | None = None
    priority: str | None = None
    budget_range: str | None = None
    notes: str | None = None
    assigned_admin_id: int | None = None
    created_at: datetime
    updated_at: datetime


class ContactLeadSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    company_name: str
    service_interest: str
    status: str
    created_at: datetime
