[![PyPI - Version](https://img.shields.io/pypi/v/wallet-rest-cli.svg)](https://pypi.org/project/wallet-rest-cli)
[![GitHub Tag](https://img.shields.io/github/v/tag/hugobatista/wallet-rest-cli?logo=github&label=latest)](https://go.hugobatista.com/gh/wallet-rest-cli/releases)
[![GHCR Tag](https://img.shields.io/github/v/tag/hugobatista/wallet-rest-cli?logo=docker&logoColor=white&label=GHCR)](https://go.hugobatista.com/gh/wallet-rest-cli/packages)
[![Test](https://go.hugobatista.com/gh/wallet-rest-cli/actions/workflows/test.yml/badge.svg)](https://go.hugobatista.com/gh/wallet-rest-cli/actions/workflows/test.yml)
[![Lint](https://go.hugobatista.com/gh/wallet-rest-cli/actions/workflows/lint.yml/badge.svg)](https://go.hugobatista.com/gh/wallet-rest-cli/actions/workflows/lint.yml)

## wallet-rest-cli

`wallet-rest-cli` is a console CLI for the BudgetBakers Wallet API. Useful for debugging or provide a CLI for your AI Agents.

Warning: This CLI is unofficial and not affiliated with BudgetBakers. Use at your own risk.

### Setup

Install the package from PyPI:

```bash
python -m pip install wallet-rest-cli
```

The CLI expects a Wallet API token from the BudgetBakers web app.

```bash
export WALLET_API_TOKEN="your-token"
wallet-rest-cli --help
```

If you prefer a local development workflow, you can still run it with `uv`:

```bash
uv run wallet-rest-cli --help
```

### Docker

Build the container image locally:

```bash
docker build -t wallet-rest-cli .
```

Run the image with your Wallet API token:

```bash
docker run --rm \
  -e WALLET_API_TOKEN="$WALLET_API_TOKEN" \
  wallet-rest-cli categories --limit 200
```

You can also use the image published to GHCR:

```bash
docker pull ghcr.io/<owner>/wallet-rest-cli:latest
docker run --rm \
  -e WALLET_API_TOKEN="$WALLET_API_TOKEN" \
  ghcr.io/hugobatista/wallet-rest-cli:latest --help
```

### Commands

- `categories` - list categories with details.
- `records` - list financial records with date, amount, category, label, and
  text filters.
- `records-by-id` - fetch records by one or more record IDs.
- `budgets` - list budgets.
- `accounts` - list accounts.
- `goals` - list goals.
- `labels` - list labels.
- `record-rules` - list automatic categorization rules.
- `standing-orders` - list recurring payments.
- `api-usage-stats` - fetch API usage statistics.

### Examples

```bash
wallet-rest-cli categories --token "$WALLET_API_TOKEN" --limit 200
wallet-rest-cli records --token "$WALLET_API_TOKEN" --record-date-from 2025-01-01 --record-date-to 2025-01-31
wallet-rest-cli records-by-id --token "$WALLET_API_TOKEN" rec_123 rec_456
wallet-rest-cli api-usage-stats --token "$WALLET_API_TOKEN" --period 30days
```

### License

This project is licensed under the MIT License. See the `LICENSE` file.
