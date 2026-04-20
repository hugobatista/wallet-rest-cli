"""HTTP client for the BudgetBakers Wallet API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


class WalletApiError(RuntimeError):
    """Raised when the Wallet API returns an error response."""


@dataclass(slots=True)
class WalletApiClient:
    """Small HTTP client for Wallet API requests."""

    base_url: str
    token: str
    timeout: float = 30.0
    transport: httpx.BaseTransport | None = None

    def get(self, path: str, params: list[tuple[str, Any]]) -> Any:
        """Execute a GET request and return the decoded JSON payload."""

        headers = {"Authorization": f"Bearer {self.token}"}
        with httpx.Client(
            base_url=self.base_url,
            headers=headers,
            timeout=self.timeout,
            transport=self.transport,
        ) as client:
            response = client.get(path, params=params)

        if response.is_success:
            return response.json()

        raise WalletApiError(self._format_error(response))

    def _format_error(self, response: httpx.Response) -> str:
        """Build a readable error message from an API response."""

        message = self._extract_message(response)
        retry_after = response.headers.get("Retry-After")

        if response.status_code == 409:
            retry_minutes = self._extract_retry_minutes(response)
            if retry_minutes is not None:
                return (
                    "Wallet data synchronization is still in progress. "
                    f"Retry in about {retry_minutes} minutes."
                )
            return "Wallet data synchronization is still in progress."

        if response.status_code == 429 and retry_after is not None:
            return (
                "Wallet API rate limit exceeded. "
                f"Retry after {retry_after} seconds."
            )

        return (
            f"Wallet API request failed with HTTP {response.status_code}: "
            f"{message}"
        )

    def _extract_message(self, response: httpx.Response) -> str:
        """Extract the API error message or fall back to the raw body."""

        try:
            payload = response.json()
        except ValueError:
            return response.text.strip() or "Unknown error"

        if isinstance(payload, dict) and "error" in payload:
            error_text = payload["error"]
            if isinstance(error_text, str) and error_text.strip():
                return error_text.strip()

        return response.text.strip() or "Unknown error"

    def _extract_retry_minutes(self, response: httpx.Response) -> int | None:
        """Extract the retry delay reported during initial sync."""

        try:
            payload = response.json()
        except ValueError:
            return None

        if not isinstance(payload, dict):
            return None

        retry_after_minutes = payload.get("retry_after_minutes")
        if isinstance(retry_after_minutes, int):
            return retry_after_minutes

        return None
