"""
Unit tests for SecurityManager sanitization, password hashing, and token handling.
"""

import pytest
from src.security import SecurityManager


def test_password_hashing_and_verification():
    raw_pw = "DevSecOps_P5_Secret#2024"
    pw_hash, salt = SecurityManager.hash_password(raw_pw)

    assert pw_hash is not None
    assert salt is not None
    assert SecurityManager.verify_password(raw_pw, pw_hash, salt) is True
    assert SecurityManager.verify_password("wrong_password", pw_hash, salt) is False


def test_password_minimum_length_validation():
    with pytest.raises(ValueError):
        SecurityManager.hash_password("12345")


def test_input_sanitization():
    xss_payload = "<script>alert('pwned')</script>"
    cleaned = SecurityManager.sanitize_input(xss_payload)

    assert "<script>" not in cleaned
    assert "&lt;script&gt;" in cleaned


def test_safe_filename_validation():
    assert SecurityManager.is_safe_filename("document.pdf") is True
    assert SecurityManager.is_safe_filename("safe_report_2024.json") is True

    # Path traversal attempts
    assert SecurityManager.is_safe_filename("../../../etc/passwd") is False
    assert SecurityManager.is_safe_filename("..\\windows\\system32") is False
    assert SecurityManager.is_safe_filename("file/name.txt") is False


def test_session_token_generation():
    token1 = SecurityManager.generate_session_token()
    token2 = SecurityManager.generate_session_token()

    assert len(token1) >= 32
    assert token1 != token2
