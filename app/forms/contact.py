from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.forms.base import FormValidationResult, validate_form
from app.forms.validators import normalize_path, normalize_phone, sanitize_multiline_text, sanitize_text


class ContactFormSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    phone: str = Field(default="", max_length=50)
    company_name: str = Field(default="", max_length=255)
    subject: str = Field(default="", max_length=255)
    message: str = Field(..., min_length=10, max_length=5000)
    service_interest: str = Field(default="", max_length=255)
    source_page: str = Field(default="/contact", max_length=255)

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

    @field_validator("company_name", "subject", "service_interest", mode="before")
    @classmethod
    def validate_optional_text(cls, value: str | None, info) -> str:
        limits = {
            "company_name": 255,
            "subject": 255,
            "service_interest": 255,
        }
        return sanitize_text(value, max_length=limits[info.field_name])

    @field_validator("message", mode="before")
    @classmethod
    def validate_message(cls, value: str | None) -> str:
        cleaned = sanitize_multiline_text(value, max_length=5000, allow_empty=False)
        if len(cleaned) < 10:
            raise ValueError("Please enter a more detailed message.")
        return cleaned

    @field_validator("source_page", mode="before")
    @classmethod
    def validate_source_page(cls, value: str | None) -> str:
        return normalize_path(value)


class ContactForm:
    @staticmethod
    def validate(data: dict[str, str]) -> FormValidationResult:
        return validate_form(ContactFormSchema, data)
