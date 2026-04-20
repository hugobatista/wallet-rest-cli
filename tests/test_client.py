"""Tests for the HTTP client."""

from __future__ import annotations

import httpx
import pytest

from wallet_rest_cli.client import WalletApiClient, WalletApiError


def test_client_returns_json_payload() -> None:
    """Successful responses should be decoded and returned."""

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer test-token"
        assert (
            str(request.url)
            == "https://example.test/v1/api/categories?limit=1"
        )
        return httpx.Response(200, json={"categories": [{"id": "cat-1"}]})

    client = WalletApiClient(
        base_url="https://example.test",
        token="test-token",
        transport=httpx.MockTransport(handler),
    )

    payload = client.get("/v1/api/categories", [("limit", 1)])

    assert payload == {"categories": [{"id": "cat-1"}]}


def test_client_raises_readable_error_for_rate_limit() -> None:
    """Rate-limit responses should raise a readable exception."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            429,
            json={"error": "Rate limit exceeded. Please try again later."},
            headers={"Retry-After": "60"},
        )

    client = WalletApiClient(
        base_url="https://example.test",
        token="test-token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(WalletApiError, match="Retry after 60 seconds"):
        client.get("/v1/api/categories", [])


def test_client_raises_readable_error_for_sync_in_progress() -> None:
    """Initial sync responses should surface the retry window."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            409,
            json={
                "error": "init_sync_in_progress",
                "retry_after_minutes": 5,
            },
        )

    client = WalletApiClient(
        base_url="https://example.test",
        token="test-token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(WalletApiError, match="Retry in about 5 minutes"):
        client.get("/v1/api/categories", [])


def test_client_formats_sync_in_progress_without_retry_minutes() -> None:
    """A 409 without retry metadata should still return a useful message."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(409, json={"error": "init_sync_in_progress"})

    client = WalletApiClient(
        base_url="https://example.test",
        token="test-token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(
        WalletApiError,
        match="Wallet data synchronization is still in progress",
    ):
        client.get("/v1/api/categories", [])


def test_client_formats_generic_api_error_message() -> None:
    """Non-rate-limit errors should include the HTTP status and payload."""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(400, json={"error": "invalid parameter"})

    client = WalletApiClient(
        base_url="https://example.test",
        token="test-token",
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(WalletApiError, match="HTTP 400: invalid parameter"):
        client.get("/v1/api/categories", [])


def test_client_extract_message_handles_plain_text_response() -> None:
    """Plain-text responses should be surfaced verbatim when possible."""

    client = WalletApiClient(
        base_url="https://example.test", token="test-token"
    )
    response = httpx.Response(
        500,
        content=b"plain text failure",
        headers={"Content-Type": "text/plain"},
    )

    assert client._extract_message(response) == "plain text failure"


def test_client_extract_message_handles_json_without_error_key() -> None:
    """JSON responses without an error field should fall back to raw text."""

    client = WalletApiClient(
        base_url="https://example.test", token="test-token"
    )
    response = httpx.Response(500, json={"message": "missing error key"})

    assert client._extract_message(response) == response.text.strip()


def test_client_extract_retry_minutes_handles_non_json_response() -> None:
    """Non-JSON sync responses should not crash the retry parsing helper."""

    client = WalletApiClient(
        base_url="https://example.test", token="test-token"
    )
    response = httpx.Response(
        409,
        content=b"not json",
        headers={"Content-Type": "text/plain"},
    )

    assert client._extract_retry_minutes(response) is None


def test_client_extract_retry_minutes_handles_non_object_json() -> None:
    """JSON arrays should be ignored by the retry parsing helper."""

    client = WalletApiClient(
        base_url="https://example.test", token="test-token"
    )
    response = httpx.Response(409, json=["unexpected", "shape"])

    assert client._extract_retry_minutes(response) is None
