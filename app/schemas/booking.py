from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _normalize_text(value: str | None, limit: int) -> str | None:
    if value is None:
        return None
    cleaned = " ".join(value.strip().split())
    return cleaned[:limit] if cleaned else None


class ConsultationBookingBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)
    company_name: str | None = Field(default=None, max_length=255)
    consultation_type: str = Field(default="strategy", min_length=2, max_length=100)
    preferred_datetime: datetime | None = None
    timezone: str = Field(default="Asia/Calcutta", min_length=2, max_length=100)
    project_details: str = Field(..., min_length=10, max_length=5000)

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Full name must contain at least 2 characters.")
        return cleaned

    @field_validator("phone", "company_name", mode="before")
    @classmethod
    def normalize_optional_text(cls, value: str | None, info) -> str | None:
        limits = {"phone": 50, "company_name": 255}
        return _normalize_text(value, limits[info.field_name])

    @field_validator("project_details")
    @classmethod
    def validate_project_details(cls, value: str) -> str:
        cleaned = value.strip()
        if len(cleaned) < 10:
            raise ValueError("Project details must contain at least 10 characters.")
        return cleaned


class ConsultationBookingCreate(ConsultationBookingBase):
    contact_lead_id: int | None = None


class ConsultationBookingUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str | None = Field(default=None, min_length=2, max_length=255)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=50)
    company_name: str | None = Field(default=None, max_length=255)
    consultation_type: str | None = Field(default=None, min_length=2, max_length=100)
    preferred_datetime: datetime | None = None
    timezone: str | None = Field(default=None, min_length=2, max_length=100)
    project_details: str | None = Field(default=None, min_length=10, max_length=5000)
    status: str | None = Field(default=None, max_length=50)
    meeting_link: str | None = Field(default=None, max_length=500)
    admin_notes: str | None = Field(default=None, max_length=5000)
    assigned_admin_id: int | None = None


class ConsultationBookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_lead_id: int | None
    assigned_admin_id: int | None
    full_name: str
    email: EmailStr
    phone: str | None
    company_name: str | None
    consultation_type: str
    preferred_datetime: datetime | None
    timezone: str
    project_details: str
    status: str
    meeting_link: str | None
    admin_notes: str | None
    created_at: datetime
    updated_at: datetime
