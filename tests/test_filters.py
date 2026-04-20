"""Tests for query parameter helpers."""

from __future__ import annotations

import pytest

from wallet_rest_cli.filters import (
    add_text_filter,
    build_api_usage_params,
    build_common_list_params,
    build_records_by_id_params,
    build_records_params,
    normalize_account_type,
    normalize_currency_code,
    normalize_ids,
    validate_period,
    validate_sort_by,
)


def test_build_common_list_params_adds_common_filters() -> None:
    """Common list filters should be translated into query parameters."""

    params = build_common_list_params(
        limit=10,
        offset=5,
        agent_hints=True,
        ids=["a", "b"],
        name="Cash",
        name_contains=None,
        name_contains_i=None,
        created_at_from="2024-01-01T00:00:00Z",
        created_at_to="2024-01-31T00:00:00Z",
        updated_at_from=None,
        updated_at_to=None,
    )

    assert params == [
        ("limit", 10),
        ("offset", 5),
        ("agentHints", True),
        ("id", "a,b"),
        ("name", "eq.Cash"),
        ("createdAt", "gte.2024-01-01T00:00:00Z"),
        ("createdAt", "lte.2024-01-31T00:00:00Z"),
    ]


def test_build_records_params_supports_record_filters() -> None:
    """Record filters should map to the Wallet API prefix syntax."""

    params = build_records_params(
        limit=25,
        offset=0,
        agent_hints=False,
        account_id="acc-1",
        category_id="cat-2",
        label_id="lbl-3",
        note=None,
        note_contains="grocer",
        note_contains_i=None,
        payee="Amazon",
        payee_contains=None,
        payee_contains_i=None,
        payer=None,
        payer_contains=None,
        payer_contains_i=None,
        amount_min="10.50",
        amount_max="20.75",
        record_date_from="2025-01-01",
        record_date_to="2025-01-31",
        created_at_from=None,
        created_at_to=None,
        updated_at_from=None,
        updated_at_to=None,
        sort_by="-recordDate",
    )

    assert params == [
        ("limit", 25),
        ("offset", 0),
        ("accountId", "acc-1"),
        ("categoryId", "cat-2"),
        ("labelId", "lbl-3"),
        ("note", "contains.grocer"),
        ("payee", "eq.Amazon"),
        ("amount", "gte.10.50"),
        ("amount", "lte.20.75"),
        ("recordDate", "gte.2025-01-01"),
        ("recordDate", "lte.2025-01-31"),
        ("sortBy", "-recordDate"),
    ]


def test_add_text_filter_rejects_multiple_modes() -> None:
    """Only one text filter mode should be allowed per field."""

    params: list[tuple[str, str | int | bool]] = []

    with pytest.raises(ValueError, match="Only one note text filter"):
        add_text_filter(params, "note", "a", "b", None)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [("currentaccount", "CurrentAccount"), ("Cash", "Cash")],
)
def test_normalize_account_type_accepts_known_values(
    raw_value: str, expected: str
) -> None:
    """Known account types should normalize to API casing."""

    assert normalize_account_type(raw_value) == expected


def test_normalize_account_type_rejects_unknown_value() -> None:
    """Unknown account types should raise a validation error."""

    with pytest.raises(ValueError, match="Invalid account type"):
        normalize_account_type("invalid")


def test_normalize_currency_code_uppercases_value() -> None:
    """Currency codes should be normalized to uppercase."""

    assert normalize_currency_code("usd") == "USD"


def test_normalize_currency_code_rejects_empty_value() -> None:
    """Empty currency codes should fail validation."""

    with pytest.raises(ValueError, match="Currency code cannot be empty"):
        normalize_currency_code("   ")


def test_normalize_ids_flattens_and_validates() -> None:
    """ID sequences should be flattened into a single CSV string."""

    assert normalize_ids(["a", "b,c"]) == "a,b,c"


def test_normalize_ids_rejects_empty_values() -> None:
    """Blank ID entries should be rejected immediately."""

    with pytest.raises(ValueError, match="ID values cannot be empty"):
        normalize_ids([""])


def test_normalize_ids_rejects_missing_ids() -> None:
    """An empty ID sequence should fail validation."""

    with pytest.raises(ValueError, match="At least one ID is required"):
        normalize_ids([])


def test_normalize_ids_rejects_too_many_values() -> None:
    """The API max of 30 IDs should be enforced locally."""

    values = [f"id-{index}" for index in range(31)]

    with pytest.raises(ValueError, match="maximum of 30 IDs"):
        normalize_ids(values)


@pytest.mark.parametrize("period", ["30days", "4weeks", "6months"])
def test_validate_period_accepts_supported_values(period: str) -> None:
    """Supported usage-stat period formats should validate."""

    validate_period(period)
    assert build_api_usage_params(period) == [("period", period)]


@pytest.mark.parametrize("period", ["", "days", "30day", "0weeks"])
def test_validate_period_rejects_invalid_values(period: str) -> None:
    """Invalid usage-stat period formats should fail fast."""

    with pytest.raises(ValueError):
        validate_period(period)


@pytest.mark.parametrize(
    "sort_by",
    ["+recordDate", "-amount", "+createdAt", "-updatedAt"],
)
def test_validate_sort_by_accepts_allowed_fields(sort_by: str) -> None:
    """Allowed sort fields should pass validation."""

    assert validate_sort_by(sort_by) == sort_by


@pytest.mark.parametrize("sort_by", ["recordDate", "+bogus"])
def test_validate_sort_by_rejects_invalid_values(sort_by: str) -> None:
    """Invalid sort directives should raise a validation error."""

    with pytest.raises(ValueError):
        validate_sort_by(sort_by)


def test_validate_sort_by_rejects_empty_value() -> None:
    """Empty sort directives should fail validation."""

    with pytest.raises(ValueError, match="Sort value cannot be empty"):
        validate_sort_by("")


def test_records_by_id_params_join_ids_and_agent_hints() -> None:
    """Records-by-id parameters should include both IDs and hints."""

    params = build_records_by_id_params(
        record_ids=["a", "b"], agent_hints=True
    )

    assert params == [("agentHints", True), ("id", "a,b")]
