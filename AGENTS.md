# wallet-rest-cli -- Agent guide

## Dev commands

```bash
uv sync                          # install all deps
uv run hatch run validate          # lint → format-check → test → typecheck
uv run hatch run test              # pytest with 100% coverage enforcement
uv run hatch run typecheck         # mypy src --strict --no-incremental

# run a single test
uv run pytest tests/test_cli.py -v
uv run pytest tests/test_client.py::test_client_returns_json_payload -v
```

## CI notes

- `lint.yml` runs `ruff check` + `ruff format --check` + `mypy` (NOT the full lint hatch script which auto-fixes)
- `test.yml` runs `pytest --cov=src/wallet_rest_cli` (without `--cov-fail-under`)
- The **full** validation pipeline (`hatch run validate`) is **not** run in CI -- run it locally before pushing
- `validate.sh` is just `hatch run validate`

## Coverage

- 100% required by config; `__init__.py` omitted from coverage by default
- No `# pragma: no cover` allowed -- refactor to test instead

## Style

- ruff (check + format) at **79 chars**
- mypy: strict, `--no-incremental`, source only (excludes tests)

## Testing patterns

- HTTP mocking: `httpx.MockTransport` -- inject as `WalletApiClient(..., transport=...)`
- CLI testing: `typer.testing.CliRunner` -- invoke `cli.app` directly
- Request capture: use `FakeClient` dataclass (see `tests/test_cli.py`)
- Parametrize liberally with `@pytest.mark.parametrize`

## Architecture

```
src/wallet_rest_cli/
├── cli.py     # Typer app — CLI commands + request orchestration
├── client.py  # WalletApiClient — httpx GET, error formatting, Bearer auth
└── filters.py # Query param builders, validators, normalizers
tests/
├── test_cli.py
├── test_client.py
└── test_filters.py
```

Entrypoint: `wallet_rest_cli.cli:main` → registered as `wallet-rest-cli` script.

## API auth

- Token via `WALLET_API_TOKEN` env var or `--token` flag
- Base URL: `https://rest.budgetbakers.com/wallet` (override via `WALLET_API_BASE_URL` or `--base-url`)
- Bearer token in `Authorization` header

## Release workflow

- Version lives in `pyproject.toml` — update both there and in `src/wallet_rest_cli/__init__.py`
- `create_draft_release` workflow: creates draft GitHub release + release branch `release/vX.Y.Z`
- On published release: `ghcr.yml` (multi-arch Docker image) + `pypi.yml` (PyPI publish via uv build)
- Docker: `python:3.13-slim`, entrypoint `wallet-rest-cli`
