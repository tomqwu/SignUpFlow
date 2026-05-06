"""Unit tests for CORS env parsing."""

import os
from unittest.mock import patch

from api.utils.cors_config import get_cors_origins


def test_default_when_unset():
    """Defaults include localhost dev origins when env is unset."""
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("CORS_ALLOWED_ORIGINS", None)
        origins = get_cors_origins()
    assert any("localhost" in o for o in origins)
    assert "http://localhost:8000" in origins


def test_default_when_empty_string():
    """Empty string falls through to defaults."""
    with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": ""}):
        origins = get_cors_origins()
    assert any("localhost" in o for o in origins)


def test_comma_separated_list():
    """Comma-separated values become a list."""
    with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": "https://a.com,https://b.com"}):
        assert get_cors_origins() == ["https://a.com", "https://b.com"]


def test_strips_whitespace():
    """Whitespace around entries is stripped."""
    with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": " https://a.com , https://b.com "}):
        assert get_cors_origins() == ["https://a.com", "https://b.com"]


def test_skips_empty_entries():
    """Empty entries from trailing commas are dropped."""
    with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": "https://a.com,,"}):
        assert get_cors_origins() == ["https://a.com"]


def test_single_value():
    """A single origin without commas works."""
    with patch.dict(os.environ, {"CORS_ALLOWED_ORIGINS": "https://prod.example.com"}):
        assert get_cors_origins() == ["https://prod.example.com"]
