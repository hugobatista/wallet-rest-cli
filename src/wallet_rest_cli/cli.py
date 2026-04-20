"""Typer-based CLI for the BudgetBakers Wallet API."""

from __future__ import annotations

import json
from typing import Any

import typer

from wallet_rest_cli.client import WalletApiClient, WalletApiError
from wallet_rest_cli.filters import (
    build_api_usage_params,
    build_common_list_params,
    build_records_by_id_params,
    build_records_params,
    normalize_account_type,
    normalize_currency_code,
)

app = typer.Typer(
    add_completion=False,
    help="Inspect BudgetBakers Wallet data.",
)

DEFAULT_BASE_URL = "https://rest.budgetbakers.com/wallet"


def main() -> None:
    """Run the CLI application."""

    app()


def create_client(token: str, base_url: str) -> WalletApiClient:
    """Create a configured Wallet API client."""

    return WalletApiClient(base_url=base_url.rstrip("/"), token=token)


def print_json(payload: Any) -> None:
    """Print a JSON payload in a readable format."""

    typer.echo(json.dumps(payload, indent=2, ensure_ascii=False))


def execute_request(
    *,
    token: str,
    base_url: str,
    path: str,
    params: list[tuple[str, Any]],
) -> None:
    """Execute an API request and print the JSON response."""

    try:
        client = create_client(token, base_url)
        payload = client.get(path, params)
    except (ValueError, WalletApiError) as error:
        typer.secho(str(error), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from error

    print_json(payload)


@app.command()
def categories(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(
        False,
        "--agent-hints/--no-agent-hints",
        help="Include structured hints in the response.",
    ),
    id_values: list[str] = typer.Option([], "--id", help="Category IDs."),
    name: str | None = typer.Option(None, help="Exact category name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for category name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for category name."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound (gte)."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound (lte)."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound (gte)."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound (lte)."
    ),
    token: str = typer.Option(
        ..., "--token", envvar="WALLET_API_TOKEN", help="Wallet API token."
    ),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL,
        "--base-url",
        envvar="WALLET_API_BASE_URL",
        help="Wallet API base URL.",
    ),
) -> None:
    """Fetch category details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )
    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/categories",
        params=params,
    )


@app.command()
def accounts(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(
        False,
        "--agent-hints/--no-agent-hints",
        help="Include structured hints in the response.",
    ),
    id_values: list[str] = typer.Option([], "--id", help="Account IDs."),
    name: str | None = typer.Option(None, help="Exact account name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for account name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for account name."
    ),
    bank_account_number: str | None = typer.Option(
        None, help="Filter by bank account number."
    ),
    account_type: str | None = typer.Option(
        None, help="Filter by account type."
    ),
    currency_code: str | None = typer.Option(
        None, help="Filter by currency code."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound (gte)."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound (lte)."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound (gte)."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound (lte)."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch account details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )
    if bank_account_number:
        params.append(("bankAccountNumber", bank_account_number))
    if account_type:
        params.append(("accountType", normalize_account_type(account_type)))
    if currency_code:
        params.append(("currencyCode", normalize_currency_code(currency_code)))

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/accounts",
        params=params,
    )


@app.command()
def budgets(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    id_values: list[str] = typer.Option([], "--id", help="Budget IDs."),
    name: str | None = typer.Option(None, help="Exact budget name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for budget name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for budget name."
    ),
    currency_code: str | None = typer.Option(
        None, help="Filter by currency code."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch budget details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )
    if currency_code:
        params.append(("currencyCode", normalize_currency_code(currency_code)))

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/budgets",
        params=params,
    )


@app.command()
def goals(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    id_values: list[str] = typer.Option([], "--id", help="Goal IDs."),
    name: str | None = typer.Option(None, help="Exact goal name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for goal name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for goal name."
    ),
    note: str | None = typer.Option(None, help="Exact goal note."),
    note_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for goal note."
    ),
    note_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for goal note."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch goal details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )
    if note:
        params.append(("note", f"eq.{note}"))
    if note_contains:
        params.append(("note", f"contains.{note_contains}"))
    if note_contains_i:
        params.append(("note", f"contains-i.{note_contains_i}"))

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/goals",
        params=params,
    )


@app.command()
def labels(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    id_values: list[str] = typer.Option([], "--id", help="Label IDs."),
    name: str | None = typer.Option(None, help="Exact label name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for label name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for label name."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch label details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/labels",
        params=params,
    )


@app.command("record-rules")
def record_rules(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    id_values: list[str] = typer.Option([], "--id", help="Rule IDs."),
    name: str | None = typer.Option(None, help="Exact rule name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for rule name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for rule name."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch record-rule details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/record-rules",
        params=params,
    )


@app.command("standing-orders")
def standing_orders(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    id_values: list[str] = typer.Option(
        [], "--id", help="Standing order IDs."
    ),
    name: str | None = typer.Option(None, help="Exact standing order name."),
    name_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for standing order name."
    ),
    name_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for standing order name."
    ),
    currency_code: str | None = typer.Option(
        None, help="Filter by currency code."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound."
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch standing-order details."""

    params = build_common_list_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        ids=id_values,
        name=name,
        name_contains=name_contains,
        name_contains_i=name_contains_i,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
    )
    if currency_code:
        params.append(("currencyCode", normalize_currency_code(currency_code)))

    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/standing-orders",
        params=params,
    )


@app.command()
def records(
    limit: int = typer.Option(30, min=1, max=200, help="Items per page."),
    offset: int = typer.Option(0, min=0, help="Items to skip."),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    account_id: str | None = typer.Option(None, help="Exact account ID."),
    category_id: str | None = typer.Option(None, help="Exact category ID."),
    label_id: str | None = typer.Option(None, help="Exact label ID."),
    note: str | None = typer.Option(None, help="Exact note filter."),
    note_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for note."
    ),
    note_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for note."
    ),
    payee: str | None = typer.Option(None, help="Exact payee filter."),
    payee_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for payee."
    ),
    payee_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for payee."
    ),
    payer: str | None = typer.Option(None, help="Exact payer filter."),
    payer_contains: str | None = typer.Option(
        None, help="Case-sensitive substring match for payer."
    ),
    payer_contains_i: str | None = typer.Option(
        None, help="Case-insensitive substring match for payer."
    ),
    amount_min: str | None = typer.Option(
        None, help="Lower bound for amount (gte)."
    ),
    amount_max: str | None = typer.Option(
        None, help="Upper bound for amount (lte)."
    ),
    record_date_from: str | None = typer.Option(
        None, help="Record-date lower bound (gte)."
    ),
    record_date_to: str | None = typer.Option(
        None, help="Record-date upper bound (lte)."
    ),
    created_at_from: str | None = typer.Option(
        None, help="Created-at lower bound (gte)."
    ),
    created_at_to: str | None = typer.Option(
        None, help="Created-at upper bound (lte)."
    ),
    updated_at_from: str | None = typer.Option(
        None, help="Updated-at lower bound (gte)."
    ),
    updated_at_to: str | None = typer.Option(
        None, help="Updated-at upper bound (lte)."
    ),
    sort_by: str = typer.Option(
        "-recordDate",
        help=(
            "Sort by +recordDate, -recordDate, +amount, -amount, "
            "+createdAt, or -updatedAt."
        ),
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch financial records."""

    params = build_records_params(
        limit=limit,
        offset=offset,
        agent_hints=agent_hints,
        account_id=account_id,
        category_id=category_id,
        label_id=label_id,
        note=note,
        note_contains=note_contains,
        note_contains_i=note_contains_i,
        payee=payee,
        payee_contains=payee_contains,
        payee_contains_i=payee_contains_i,
        payer=payer,
        payer_contains=payer_contains,
        payer_contains_i=payer_contains_i,
        amount_min=amount_min,
        amount_max=amount_max,
        record_date_from=record_date_from,
        record_date_to=record_date_to,
        created_at_from=created_at_from,
        created_at_to=created_at_to,
        updated_at_from=updated_at_from,
        updated_at_to=updated_at_to,
        sort_by=sort_by,
    )
    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/records",
        params=params,
    )


@app.command("records-by-id")
def records_by_id(
    record_ids: list[str] = typer.Argument(
        ..., help="One or more record IDs to fetch."
    ),
    agent_hints: bool = typer.Option(False, "--agent-hints/--no-agent-hints"),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch records by their IDs."""

    params = build_records_by_id_params(
        record_ids=record_ids, agent_hints=agent_hints
    )
    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/records/by-id",
        params=params,
    )


@app.command("api-usage-stats")
def api_usage_stats(
    period: str = typer.Option(
        "30days",
        help="Period to query, such as 30days, 4weeks, or 6months.",
    ),
    token: str = typer.Option(..., "--token", envvar="WALLET_API_TOKEN"),
    base_url: str = typer.Option(
        DEFAULT_BASE_URL, "--base-url", envvar="WALLET_API_BASE_URL"
    ),
) -> None:
    """Fetch API usage statistics."""

    params = build_api_usage_params(period)
    execute_request(
        token=token,
        base_url=base_url,
        path="/v1/api/api-usage/stats",
        params=params,
    )
