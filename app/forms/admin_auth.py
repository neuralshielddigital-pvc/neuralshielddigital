from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.forms.base import FormValidationResult, validate_form
from app.forms.validators import sanitize_text


class AdminLoginFormSchema(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password", mode="before")
    @classmethod
    def validate_password(cls, value: str | None) -> str:
        cleaned = sanitize_text(value, max_length=128, allow_empty=False)
        if len(cleaned) < 8:
            raise ValueError("Please enter your password.")
        return cleaned


class AdminLoginForm:
    @staticmethod
    def validate(data: dict[str, str]) -> FormValidationResult:
        return validate_form(AdminLoginFormSchema, data)
