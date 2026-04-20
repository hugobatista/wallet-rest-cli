"""Tests for the CLI entry points."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

import pytest
import typer
from typer.testing import CliRunner

from wallet_rest_cli import cli

runner = CliRunner()


@dataclass
class FakeClient:
    """Capture requests made by the CLI during tests."""

    calls: list[tuple[str, list[tuple[str, Any]]]]
    payload: dict[str, Any]

    def get(self, path: str, params: list[tuple[str, Any]]) -> dict[str, Any]:
        self.calls.append((path, params))
        return self.payload


def test_main_invokes_app(monkeypatch: pytest.MonkeyPatch) -> None:
    """The package entry point should delegate to the Typer app."""

    called = {"value": False}

    def fake_app() -> None:
        called["value"] = True

    monkeypatch.setattr(cli, "app", fake_app)

    cli.main()

    assert called["value"] is True


def test_create_client_strips_trailing_slash() -> None:
    """The client factory should normalize the base URL."""

    client = cli.create_client("test-token", "https://example.test/")

    assert client.base_url == "https://example.test"


def test_print_json_writes_indented_output(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """JSON output should be pretty-printed for console readability."""

    cli.print_json({"value": 1})

    captured = capsys.readouterr()
    assert captured.out == '{\n  "value": 1\n}\n'


def test_execute_request_surfaces_client_errors(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Client construction failures should be surfaced as CLI exits."""

    def raise_error(_: str, __: str) -> None:
        raise ValueError("bad token")

    monkeypatch.setattr(cli, "create_client", raise_error)

    with pytest.raises(typer.Exit) as exit_error:
        cli.execute_request(
            token="test-token",
            base_url="https://example.test",
            path="/v1/api/categories",
            params=[],
        )

    assert exit_error.value.exit_code == 1


def test_categories_command_builds_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Categories should translate options into API query params."""

    fake_client = FakeClient([], {"categories": [{"id": "cat-1"}]})
    monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

    result = runner.invoke(
        cli.app,
        [
            "categories",
            "--token",
            "test-token",
            "--limit",
            "7",
            "--offset",
            "3",
            "--id",
            "cat-1",
            "--name",
            "Food",
            "--created-at-from",
            "2024-01-01T00:00:00Z",
        ],
    )

    assert result.exit_code == 0
    assert json.loads(result.stdout) == {"categories": [{"id": "cat-1"}]}
    assert fake_client.calls == [
        (
            "/v1/api/categories",
            [
                ("limit", 7),
                ("offset", 3),
                ("id", "cat-1"),
                ("name", "eq.Food"),
                ("createdAt", "gte.2024-01-01T00:00:00Z"),
            ],
        )
    ]


def test_list_commands_cover_all_resource_endpoints(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Every list endpoint should call the correct API path."""

    cases = [
        (
            "accounts",
            [
                "--bank-account-number",
                "1234",
                "--account-type",
                "cash",
                "--currency-code",
                "usd",
            ],
            "/v1/api/accounts",
        ),
        ("budgets", ["--currency-code", "usd"], "/v1/api/budgets"),
        (
            "goals",
            [
                "--note",
                "vacation",
                "--note-contains",
                "vacation",
                "--note-contains-i",
                "trip",
            ],
            "/v1/api/goals",
        ),
        ("labels", [], "/v1/api/labels"),
        ("record-rules", [], "/v1/api/record-rules"),
        (
            "standing-orders",
            ["--currency-code", "eur"],
            "/v1/api/standing-orders",
        ),
    ]

    for command_name, extra_args, expected_path in cases:
        fake_client = FakeClient([], {command_name: []})
        monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

        result = runner.invoke(
            cli.app,
            [command_name, "--token", "test-token", *extra_args],
        )

        assert result.exit_code == 0
        assert fake_client.calls[0][0] == expected_path


def test_accounts_command_normalizes_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Accounts should normalize account type and currency code."""

    fake_client = FakeClient([], {"accounts": []})
    monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

    result = runner.invoke(
        cli.app,
        [
            "accounts",
            "--token",
            "test-token",
            "--account-type",
            "currentaccount",
            "--currency-code",
            "usd",
        ],
    )

    assert result.exit_code == 0
    assert fake_client.calls == [
        (
            "/v1/api/accounts",
            [
                ("limit", 30),
                ("offset", 0),
                ("accountType", "CurrentAccount"),
                ("currencyCode", "USD"),
            ],
        )
    ]


def test_records_command_supports_full_filter_surface(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Records should send the API's supported filter prefixes."""

    fake_client = FakeClient([], {"records": []})
    monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

    result = runner.invoke(
        cli.app,
        [
            "records",
            "--token",
            "test-token",
            "--account-id",
            "acc-1",
            "--category-id",
            "cat-1",
            "--label-id",
            "lbl-1",
            "--note-contains",
            "grocer",
            "--payee",
            "Amazon",
            "--amount-min",
            "10.50",
            "--amount-max",
            "20.75",
            "--record-date-from",
            "2025-01-01",
            "--record-date-to",
            "2025-01-31",
            "--sort-by",
            "+amount",
        ],
    )

    assert result.exit_code == 0
    assert fake_client.calls == [
        (
            "/v1/api/records",
            [
                ("limit", 30),
                ("offset", 0),
                ("accountId", "acc-1"),
                ("categoryId", "cat-1"),
                ("labelId", "lbl-1"),
                ("note", "contains.grocer"),
                ("payee", "eq.Amazon"),
                ("amount", "gte.10.50"),
                ("amount", "lte.20.75"),
                ("recordDate", "gte.2025-01-01"),
                ("recordDate", "lte.2025-01-31"),
                ("sortBy", "+amount"),
            ],
        )
    ]


def test_records_by_id_command_joins_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Records-by-id should accept multiple positional IDs."""

    fake_client = FakeClient([], {"count": 2, "records": []})
    monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

    result = runner.invoke(
        cli.app,
        [
            "records-by-id",
            "--token",
            "test-token",
            "rec-1",
            "rec-2",
        ],
    )

    assert result.exit_code == 0
    assert fake_client.calls == [
        (
            "/v1/api/records/by-id",
            [("id", "rec-1,rec-2")],
        )
    ]


def test_api_usage_stats_command_validates_period(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """API usage stats should validate the period and call the endpoint."""

    fake_client = FakeClient([], {"period": "30days", "usage": []})
    monkeypatch.setattr(cli, "create_client", lambda *_: fake_client)

    result = runner.invoke(
        cli.app,
        [
            "api-usage-stats",
            "--token",
            "test-token",
            "--period",
            "4weeks",
        ],
    )

    assert result.exit_code == 0
    assert fake_client.calls == [
        ("/v1/api/api-usage/stats", [("period", "4weeks")])
    ]
