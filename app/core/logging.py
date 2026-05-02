from __future__ import annotations

import json
import logging
import logging.config
from datetime import datetime, timezone

from app.core.config import Settings


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("environment", "debug", "domain", "path", "method", "status_code", "detail", "errors"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def configure_logging(settings: Settings) -> None:
    formatter_name = "json" if settings.log_json else "standard"
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            },
            "json": {
                "()": JsonFormatter,
            },
        },
        "handlers": {
            "default": {
                "class": "logging.StreamHandler",
                "formatter": formatter_name,
                "level": settings.log_level,
            },
        },
        "root": {
            "handlers": ["default"],
            "level": settings.log_level,
        },
        "loggers": {
            "uvicorn": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
            "uvicorn.error": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
            "uvicorn.access": {"level": settings.log_level, "handlers": ["default"], "propagate": False},
            "sqlalchemy.engine": {
                "level": "WARNING" if not settings.db_echo else "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
        },
    }
    logging.config.dictConfig(config)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
