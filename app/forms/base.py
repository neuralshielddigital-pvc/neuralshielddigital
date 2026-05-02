from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError


ModelT = TypeVar("ModelT", bound=BaseModel)


@dataclass(slots=True)
class FormValidationResult:
    is_valid: bool
    cleaned_data: dict[str, Any] = field(default_factory=dict)
    errors: dict[str, list[str]] = field(default_factory=dict)

    @property
    def first_error(self) -> str | None:
        for messages in self.errors.values():
            if messages:
                return messages[0]
        return None


def validation_error_to_dict(exc: ValidationError) -> dict[str, list[str]]:
    errors: dict[str, list[str]] = {}
    for item in exc.errors():
        loc = item.get("loc", ("form",))
        field_name = str(loc[-1]) if loc else "form"
        message = str(item.get("msg", "Invalid value."))
        if message.startswith("Value error, "):
            message = message.replace("Value error, ", "", 1)
        errors.setdefault(field_name, []).append(message)
    return errors


def validate_form(model_class: type[ModelT], data: dict[str, Any]) -> FormValidationResult:
    try:
        form = model_class.model_validate(data)
    except ValidationError as exc:
        return FormValidationResult(
            is_valid=False,
            cleaned_data=data,
            errors=validation_error_to_dict(exc),
        )

    return FormValidationResult(
        is_valid=True,
        cleaned_data=form.model_dump(),
        errors={},
    )
