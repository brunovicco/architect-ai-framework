import pytest

from arquiteto.providers import OpenAICompatibleAdapter, assert_safe_base_url


def test_rejects_non_https():
    with pytest.raises(ValueError, match="https"):
        assert_safe_base_url("http://example.com")


def test_rejects_localhost():
    with pytest.raises(ValueError, match="localhost"):
        assert_safe_base_url("https://localhost")


def test_rejects_loopback_ip():
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://127.0.0.1")


def test_rejects_private_ip():
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://10.0.0.1")


def test_rejects_cloud_metadata_address():
    with pytest.raises(ValueError, match="non-public"):
        assert_safe_base_url("https://169.254.169.254")


def test_accepts_public_https_host():
    assert_safe_base_url("https://example.com")


def test_adapter_constructor_runs_the_same_guard():
    with pytest.raises(ValueError, match="non-public"):
        OpenAICompatibleAdapter(base_url="https://127.0.0.1", api_key="x", model="x")
