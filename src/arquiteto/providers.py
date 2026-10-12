"""Optional provider boundary for model-assisted features (e.g. an AI review
of a generated plan).

The ARQUITETO/ARCHITECT decision engine does not depend on this module and
never calls a model itself — see `docs/PROVIDER_NEUTRALITY.md`. This module
exists so an *optional* reviewer can be wired into the UI without coupling
the framework to a specific model vendor.

Any new adapter added here, or any change to `OpenAICompatibleAdapter`, must
satisfy the checklist in `docs/PROVIDERS_SECURITY_CHECKLIST.md` (OWASP LLM
Top 10 / MITRE ATLAS) before being merged.
"""

import ipaddress
import json
import socket
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


class ModelAdapter(Protocol):
    """Minimal provider-neutral contract for an optional model runtime."""

    def generate(self, system: str, user: str) -> str:
        """Return a text response for the supplied system/user input."""
        ...


class AdapterError(RuntimeError):
    """Raised when a ModelAdapter cannot produce a response."""


def assert_safe_base_url(url: str) -> None:
    """Reject a `base_url` that could be used for SSRF against internal or
    cloud infrastructure (e.g. the 169.254.169.254 cloud metadata endpoint).

    Only `https://` URLs whose hostname resolves exclusively to public,
    non-reserved addresses are allowed. This is a best-effort, defense-in-depth
    check (DNS can still change between this check and the actual request —
    a classic TOCTOU/"rebinding" limitation of any userland SSRF guard); it is
    not a substitute for running this call from a network-isolated egress path
    in a real deployment.
    """
    parsed = urlsplit(url)
    if parsed.scheme != "https":
        raise ValueError("base_url must use https://")
    hostname = parsed.hostname
    if not hostname:
        raise ValueError("base_url must include a hostname")
    if hostname.lower() == "localhost":
        raise ValueError("base_url may not point at localhost")

    try:
        infos = socket.getaddrinfo(hostname, None)
    except OSError as exc:
        raise ValueError(f"could not resolve base_url host: {hostname}") from exc

    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast or ip.is_unspecified:
            raise ValueError(f"base_url resolves to a non-public address ({ip}); refusing to call it")


class OpenAICompatibleAdapter:
    """Generic `ModelAdapter` for any OpenAI-chat-completions-compatible
    endpoint.

    This is intentionally vendor-neutral: the exact same class works with
    OpenAI, an OpenAI-compatible gateway, or a self-hosted server (Ollama,
    vLLM, LM Studio, ...) — the caller supplies `base_url`, `api_key` and
    `model`; nothing here is hardcoded to one vendor. `base_url` is validated
    by `assert_safe_base_url` to guard against SSRF, since in `app.py` this
    value comes from the (untrusted) visitor of a publicly hosted instance.
    """

    def __init__(self, base_url: str, api_key: str, model: str, timeout: float = 30.0) -> None:
        assert_safe_base_url(base_url)
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout

    def generate(self, system: str, user: str) -> str:
        payload = json.dumps(
            {
                "model": self._model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
            }
        ).encode("utf-8")
        request = Request(
            f"{self._base_url}/chat/completions",
            data=payload,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self._api_key}",
            },
        )
        try:
            with urlopen(request, timeout=self._timeout) as response:  # noqa: S310 - base_url is validated above
                body = json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError) as exc:
            raise AdapterError(f"model endpoint request failed: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise AdapterError(f"model endpoint returned an unparseable response: {exc}") from exc

        try:
            return body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise AdapterError("model endpoint response did not contain a message") from exc
