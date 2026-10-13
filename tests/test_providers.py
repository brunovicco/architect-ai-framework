"""Tests for the SSRF guard and error handling in `architect.providers`."""

import pytest

from architect.providers import AdapterError, OpenAICompatibleAdapter, assert_safe_base_url


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


def test_generate_wraps_timeout_in_adapter_error(monkeypatch):
    """A socket timeout during generate() is wrapped in AdapterError, never left
    to escape as a raw TimeoutError and crash the caller (regression: a slow
    hosted model used to crash the whole Streamlit app instead of showing a
    clean error, since TimeoutError isn't always wrapped by urllib).
    """
    def _raise_timeout(*args, **kwargs):
        raise TimeoutError("timed out")

    monkeypatch.setattr("architect.providers.urlopen", _raise_timeout)
    adapter = OpenAICompatibleAdapter(base_url="https://example.com", api_key="x", model="x")
    with pytest.raises(AdapterError, match="model endpoint request failed"):
        adapter.generate(system="s", user="u")


def test_redirect_cannot_forward_credentials_to_private_target():
    from email.message import Message
    from io import BytesIO
    from urllib.error import HTTPError
    from urllib.request import Request

    from architect.providers import _RejectRedirects

    request = Request('https://example.com/chat/completions', data=b'plan',
                      headers={'Authorization': 'Bearer synthetic-test-key'})
    headers = Message()
    headers['Location'] = 'http://127.0.0.1/private'
    with pytest.raises(HTTPError):
        _RejectRedirects().http_error_302(request, BytesIO(), 302, 'Found', headers)
