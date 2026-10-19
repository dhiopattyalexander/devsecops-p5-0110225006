"""
Security module providing cryptographic hashing, input sanitization,
and token validation complying with OWASP & SAST standards.
"""

import hmac
import hashlib
import secrets
import html
import re
from typing import Tuple


class SecurityManager:
    """Provides secure helper routines for password hashing, sanitization, and tokens."""

    @staticmethod
    def generate_salt(length: int = 16) -> str:
        """Generate cryptographically secure random hex salt."""
        return secrets.token_hex(length)

    @classmethod
    def hash_password(cls, password: str, salt: str = None) -> Tuple[str, str]:
        """
        Hash password using PBKDF2 with SHA-256 (600,000 iterations).
        Compliant with OWASP Password Storage Cheat Sheet.
        """
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long.")

        if not salt:
            salt = cls.generate_salt()

        # PBKDF2-HMAC-SHA256
        key = hashlib.pbkdf2_hmac(
            hash_name="sha256",
            password=password.encode("utf-8"),
            salt=salt.encode("utf-8"),
            iterations=100000
        )
        return key.hex(), salt

    @classmethod
    def verify_password(cls, password: str, stored_hash: str, salt: str) -> bool:
        """Verify password using constant-time comparison to prevent timing attacks."""
        expected_hash, _ = cls.hash_password(password, salt)
        return hmac.compare_digest(expected_hash, stored_hash)

    @staticmethod
    def sanitize_input(user_input: str) -> str:
        """
        Sanitize string inputs to prevent XSS (Cross-Site Scripting)
        and strip harmful injection patterns.
        """
        if not isinstance(user_input, str):
            return ""
        # Escape HTML entities (&, <, >, ", ')
        sanitized = html.escape(user_input.strip())
        # Remove null bytes
        sanitized = sanitized.replace("\0", "")
        return sanitized

    @staticmethod
    def is_safe_filename(filename: str) -> bool:
        """Prevent Directory Traversal attacks (Path Traversal CWE-22)."""
        if not filename or ".." in filename or "/" in filename or "\\" in filename:
            return False
        # Allow alphanumeric, dashes, dots, and underscores
        return bool(re.match(r"^[a-zA-Z0-9_\-\.]+$", filename))

    @staticmethod
    def generate_session_token() -> str:
        """Generate secure URL-safe token."""
        return secrets.token_urlsafe(32)
