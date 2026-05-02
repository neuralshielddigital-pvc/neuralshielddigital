from __future__ import annotations

from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session


class ServiceError(Exception):
    """Base service-layer exception."""


class NotFoundError(ServiceError):
    """Raised when a requested database record does not exist."""


class ConflictError(ServiceError):
    """Raised when a uniqueness or state conflict occurs."""


class AuthenticationServiceError(ServiceError):
    """Raised when authentication fails."""


class BaseService:
    def __init__(self, db: Session):
        self.db = db

    def add_and_commit(self, instance: Any) -> Any:
        try:
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            return instance
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def commit(self) -> None:
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise

    def delete_and_commit(self, instance: Any) -> None:
        try:
            self.db.delete(instance)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
