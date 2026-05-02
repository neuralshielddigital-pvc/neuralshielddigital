from __future__ import annotations

import base64
import hashlib
import os
import secrets
from typing import Any

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.core.config import get_settings

settings = get_settings()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    password_bytes = password.encode("utf-8")
    dk = hashlib.pbkdf2_hmac("sha256", password_bytes, salt, 260000)
    return "pbkdf2_sha256$260000$" + base64.b64encode(salt).decode() + "$" + base64.b64encode(dk).decode()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iterations, salt_b64, hash_b64 = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False

        salt = base64.b64decode(salt_b64)
        expected_hash = base64.b64decode(hash_b64)
        test_hash = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            int(iterations),
        )
        return secrets.compare_digest(test_hash, expected_hash)
    except Exception:
        return False


def _session_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.secret_key, salt="admin-session")


def _csrf_serializer() -> URLSafeTimedSerializer:
    return URLSafeTimedSerializer(settings.csrf_secret_key, salt="csrf-token")


def create_admin_session_payload(admin_id: int, email: str, role: str) -> dict[str, Any]:
    return {"id": admin_id, "email": email, "role": role}


def sign_admin_session(payload: dict[str, Any]) -> str:
    return _session_serializer().dumps(payload)


def verify_admin_session(token: str, max_age: int | None = None) -> dict[str, Any] | None:
    try:
        return _session_serializer().loads(
            token,
            max_age=max_age or settings.session_max_age_seconds,
        )
    except (BadSignature, SignatureExpired):
        return None


def create_csrf_token(value: str) -> str:
    return _csrf_serializer().dumps({"value": value})


def verify_csrf_token(token: str, value: str, max_age: int = 3600) -> bool:
    try:
        payload = _csrf_serializer().loads(token, max_age=max_age)
    except (BadSignature, SignatureExpired):
        return False

    return payload.get("value") == value