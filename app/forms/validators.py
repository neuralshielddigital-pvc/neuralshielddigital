from __future__ import annotations

import re
from html import escape


MULTISPACE_RE = re.compile(r"\s+")
PHONE_RE = re.compile(r"^[0-9+\-() ]+$")
SLUG_FRAGMENT_RE = re.compile(r"^[a-zA-Z0-9/_\-]+$")


def sanitize_text(value: str | None, *, max_length: int, allow_empty: bool = True) -> str:
    if value is None:
        return ""
    cleaned = MULTISPACE_RE.sub(" ", value.strip())
    cleaned = escape(cleaned, quote=False)
    cleaned = cleaned[:max_length]
    if not allow_empty and not cleaned:
        raise ValueError("This field is required.")
    return cleaned


def sanitize_multiline_text(value: str | None, *, max_length: int, allow_empty: bool = True) -> str:
    if value is None:
        return ""
    lines = [line.strip() for line in value.replace("\r\n", "\n").split("\n")]
    cleaned = "\n".join(line for line in lines if line)
    cleaned = escape(cleaned, quote=False)
    cleaned = cleaned[:max_length]
    if not allow_empty and not cleaned:
        raise ValueError("This field is required.")
    return cleaned


def normalize_phone(value: str | None) -> str:
    cleaned = sanitize_text(value, max_length=50)
    if cleaned and not PHONE_RE.fullmatch(cleaned):
        raise ValueError("Enter a valid phone or WhatsApp number.")
    return cleaned


def normalize_path(value: str | None) -> str:
    cleaned = sanitize_text(value, max_length=255, allow_empty=False)
    if not cleaned.startswith("/"):
        raise ValueError("Invalid page source.")
    if not SLUG_FRAGMENT_RE.fullmatch(cleaned):
        raise ValueError("Invalid page source.")
    return cleaned
