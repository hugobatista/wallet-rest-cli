"""Query parameter builders for Wallet API endpoints."""

from __future__ import annotations

from collections.abc import Sequence

QueryParams = list[tuple[str, str | int | bool]]

_ACCOUNT_TYPES = {
    "general": "General",
    "cash": "Cash",
    "currentaccount": "CurrentAccount",
    "creditcard": "CreditCard",
    "savingaccount": "SavingAccount",
    "bonus": "Bonus",
    "insurance": "Insurance",
    "investment": "Investment",
    "loan": "Loan",
    "mortgage": "Mortgage",
    "overdraft": "Overdraft",
}

_ALLOWED_RECORD_SORT_FIELDS = {
    "recordDate",
    "amount",
    "createdAt",
    "updatedAt",
}


def build_common_list_params(
    *,
    limit: int,
    offset: int,
    agent_hints: bool,
    ids: Sequence[str] | None = None,
    name: str | None = None,
    name_contains: str | None = None,
    name_contains_i: str | None = None,
    created_at_from: str | None = None,
    created_at_to: str | None = None,
    updated_at_from: str | None = None,
    updated_at_to: str | None = None,
) -> QueryParams:
    """Build query parameters shared by list endpoints."""

    params: QueryParams = [("limit", limit), ("offset", offset)]
    add_bool_param(params, "agentHints", agent_hints)
    add_id_list_param(params, ids)
    add_text_filter(params, "name", name, name_contains, name_contains_i)
    add_range_param(params, "createdAt", created_at_from, created_at_to)
    add_range_param(params, "updatedAt", updated_at_from, updated_at_to)
    return params


def add_bool_param(params: QueryParams, name: str, enabled: bool) -> None:
    """Append a boolean query parameter when it is enabled."""

    if enabled:
        params.append((name, True))


def add_id_list_param(params: QueryParams, ids: Sequence[str] | None) -> None:
    """Append a comma-separated ID list when IDs are provided."""

    if ids is None or len(ids) == 0:
        return

    normalized_ids = normalize_ids(ids)
    params.append(("id", normalized_ids))


def add_text_filter(
    params: QueryParams,
    field_name: str,
    exact: str | None,
    contains: str | None,
    contains_i: str | None,
) -> None:
    """Append a text filter using the API prefix syntax."""

    selected_filters = [
        ("eq", exact),
        ("contains", contains),
        ("contains-i", contains_i),
    ]
    chosen = [(prefix, value) for prefix, value in selected_filters if value]

    if len(chosen) > 1:
        raise ValueError(
            f"Only one {field_name} text filter can be used at a time."
        )

    if chosen:
        prefix, value = chosen[0]
        params.append((field_name, f"{prefix}.{value}"))


def add_range_param(
    params: QueryParams,
    field_name: str,
    minimum: str | None,
    maximum: str | None,
) -> None:
    """Append zero, one, or two range filters for a field."""

    if minimum:
        params.append((field_name, f"gte.{minimum}"))

    if maximum:
        params.append((field_name, f"lte.{maximum}"))


def build_records_params(
    *,
    limit: int,
    offset: int,
    agent_hints: bool,
    account_id: str | None,
    category_id: str | None,
    label_id: str | None,
    note: str | None,
    note_contains: str | None,
    note_contains_i: str | None,
    payee: str | None,
    payee_contains: str | None,
    payee_contains_i: str | None,
    payer: str | None,
    payer_contains: str | None,
    payer_contains_i: str | None,
    amount_min: str | None,
    amount_max: str | None,
    record_date_from: str | None,
    record_date_to: str | None,
    created_at_from: str | None,
    created_at_to: str | None,
    updated_at_from: str | None,
    updated_at_to: str | None,
    sort_by: str | None,
) -> QueryParams:
    """Build query parameters for the records endpoint."""

    params: QueryParams = [("limit", limit), ("offset", offset)]
    add_bool_param(params, "agentHints", agent_hints)

    if account_id:
        params.append(("accountId", account_id))

    if category_id:
        params.append(("categoryId", category_id))

    if label_id:
        params.append(("labelId", label_id))

    add_text_filter(params, "note", note, note_contains, note_contains_i)
    add_text_filter(params, "payee", payee, payee_contains, payee_contains_i)
    add_text_filter(params, "payer", payer, payer_contains, payer_contains_i)
    add_range_param(params, "amount", amount_min, amount_max)
    add_range_param(params, "recordDate", record_date_from, record_date_to)
    add_range_param(params, "createdAt", created_at_from, created_at_to)
    add_range_param(params, "updatedAt", updated_at_from, updated_at_to)

    if sort_by:
        params.append(("sortBy", validate_sort_by(sort_by)))

    return params


def build_records_by_id_params(
    *,
    record_ids: Sequence[str],
    agent_hints: bool,
) -> QueryParams:
    """Build query parameters for the records-by-id endpoint."""

    params: QueryParams = []
    add_bool_param(params, "agentHints", agent_hints)
    params.append(("id", normalize_ids(record_ids)))
    return params


def build_api_usage_params(period: str) -> QueryParams:
    """Build query parameters for the API usage statistics endpoint."""

    validate_period(period)
    return [("period", period)]


def normalize_account_type(account_type: str) -> str:
    """Normalize account type input to the API's canonical casing."""

    normalized = _ACCOUNT_TYPES.get(account_type.replace(" ", "").lower())
    if normalized is None:
        allowed_types = ", ".join(_ACCOUNT_TYPES.values())
        raise ValueError(
            "Invalid account type. Allowed values are: " f"{allowed_types}."
        )

    return normalized


def normalize_currency_code(currency_code: str) -> str:
    """Normalize a currency code to uppercase."""

    normalized = currency_code.strip().upper()
    if not normalized:
        raise ValueError("Currency code cannot be empty.")

    return normalized


def normalize_ids(values: Sequence[str]) -> str:
    """Flatten and validate a list of IDs into a CSV string."""

    ids: list[str] = []
    for raw_value in values:
        for value in raw_value.split(","):
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("ID values cannot be empty.")
            ids.append(trimmed)

    if not ids:
        raise ValueError("At least one ID is required.")

    if len(ids) > 30:
        raise ValueError("A maximum of 30 IDs can be sent at once.")

    return ",".join(ids)


def validate_period(period: str) -> None:
    """Validate the API usage period format."""

    if not period:
        raise ValueError("Period cannot be empty.")

    suffix = (
        period.removesuffix("days")
        .removesuffix("weeks")
        .removesuffix("months")
    )
    if suffix == period:
        raise ValueError("Period must end with 'days', 'weeks', or 'months'.")

    if not suffix.isdigit():
        raise ValueError("Period must start with a positive integer.")

    if int(suffix) <= 0:
        raise ValueError("Period must be greater than zero.")


def validate_sort_by(sort_by: str) -> str:
    """Validate the records sort field and direction."""

    if not sort_by:
        raise ValueError("Sort value cannot be empty.")

    direction = sort_by[0]
    field_name = sort_by[1:] if direction in {"+", "-"} else sort_by

    if field_name not in _ALLOWED_RECORD_SORT_FIELDS:
        allowed_fields = ", ".join(sorted(_ALLOWED_RECORD_SORT_FIELDS))
        raise ValueError(
            f"Invalid sort field. Allowed fields are: {allowed_fields}."
        )

    if direction not in {"+", "-"}:
        raise ValueError("Sort values must start with '+' or '-'.")

    return sort_by
