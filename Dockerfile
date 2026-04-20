FROM python:3.13-slim

LABEL org.opencontainers.image.title="wallet-rest-cli"
LABEL org.opencontainers.image.description="Console CLI for the BudgetBakers Wallet API"
LABEL org.opencontainers.image.source=https://go.hugobatista.com/gh/wallet-rest-cli
LABEL security.scan="true"
LABEL maintainer="Hugo Batista <mail@hugobatista.com>"


ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_ROOT_USER_ACTION=ignore

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src

RUN python -m pip install --no-cache-dir --upgrade pip \
 && python -m pip install --no-cache-dir /app

RUN addgroup --system wallet \
 && adduser --system --ingroup wallet wallet \
 && chown -R wallet:wallet /app

USER wallet

ENTRYPOINT ["wallet-rest-cli"]