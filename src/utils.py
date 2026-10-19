"""
Utility helper functions for logging, response formatting, and validations.
"""

import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, Tuple


def setup_logger(name: str = "secure_app") -> logging.Logger:
    """Configure structured logger for audit and system tracking."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


def format_response(
    success: bool,
    data: Any = None,
    message: str = "",
    status_code: int = 200
) -> Tuple[Dict[str, Any], int]:
    """Standardized API response wrapper."""
    payload = {
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": message,
        "data": data if data is not None else {}
    }
    return payload, status_code


def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Tuple[bool, str]:
    """Validate presence of required payload keys."""
    if not isinstance(data, dict):
        return False, "Payload must be a valid JSON object."

    missing = [field for field in required_fields if field not in data or data[field] is None]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    return True, ""
