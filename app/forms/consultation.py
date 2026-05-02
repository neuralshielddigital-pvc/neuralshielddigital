from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.forms.base import FormValidationResult, validate_form
from app.forms.validators import normalize_phone, sanitize_multiline_text, sanitize_text


class ConsultationBookingFormSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(default="", max_length=50)
    company_name: str = Field(default="", max_length=255)
    consultation_type: str = Field(default="strategy", min_length=2, max_length=100)
    preferred_datetime: datetime | None = None
    timezone: str = Field(default="Asia/Calcutta", min_length=2, max_length=100)
    project_details: str = Field(..., min_length=10, max_length=5000)

    @field_validator("full_name", mode="before")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str:
        cleaned = sanitize_text(value, max_length=255, allow_empty=False)
        if len(cleaned) < 2:
            raise ValueError("Please enter your full name.")
        return cleaned

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, value: str | None) -> str:
        return normalize_phone(value)

    @field_validator("company_name", "consultation_type", "timezone", mode="before")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str:
        limits = {
            "company_name": 255,
            "consultation_type": 100,
            "timezone": 100,
        }
        allow_empty = info.field_name != "timezone"
        return sanitize_text(value, max_length=limits[info.field_name], allow_empty=allow_empty)

    @field_validator("project_details", mode="before")
    @classmethod
    def validate_project_details(cls, value: str | None) -> str:
        cleaned = sanitize_multiline_text(value, max_length=5000, allow_empty=False)
        if len(cleaned) < 10:
            raise ValueError("Please provide some project details before submitting.")
        return cleaned


class ConsultationBookingForm:
    @staticmethod
    def validate(data: dict[str, str]) -> FormValidationResult:
        return validate_form(ConsultationBookingFormSchema, data)
