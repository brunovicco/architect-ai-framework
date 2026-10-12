"""Tests for the SSRF guard in `architect.providers`."""

import pytest

from architect.providers import OpenAICompatibleAdapter, assert_safe_base_url


def test_rejects_non_https():
    """A non-https scheme is rejected."""
    with pytest.raises(ValueError, match="https"):
        assert_safe_base_url("http://example.com")


def test_rejects_localhost():
    """The literal hostname "localhost" is rejected."""
    with pytest.raises(ValueError, match="localhost"):
        assert_safe_base_url("https://localhost")


def test_rejects_loopback_ip():
    """A loopback address (127.0.0.1) is rejected."""
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://127.0.0.1")


def test_rejects_private_ip():
    """A private-range address (10.0.0.1) is rejected."""
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://10.0.0.1")


def test_rejects_cloud_metadata_address():
    """The cloud metadata address (169.254.169.254) is rejected."""
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://169.254.169.254")


def test_accepts_public_https_host():
    """A public https hostname passes the guard without raising."""
    assert_safe_base_url("https://example.com")


def test_adapter_constructor_runs_the_same_guard():
    """OpenAICompatibleAdapter.__init__ validates base_url before storing it."""
    with pytest.raises(ValueError, match="non-public"):
        OpenAICompatibleAdapter(base_url="https://127.0.0.1", api_key="x", model="x")
