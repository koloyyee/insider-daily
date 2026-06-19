# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
# Run locally with uvicorn
uv run uvicorn app.main:app --reload

# Run tests
uv run pytest

# Run a single test
uv run pytest app/main_test.py::test_sanity -v

# Build Tailwind CSS
npx tailwindcss -i app/static/input.css -o app/static/output.css --watch

# Docker (local dev)
make docker-local

# Docker (production with nginx)
make docker-remote

# Docker (single container dev)
make docker-dev

# Regenerate ticker enum from SEC
uv run python -c "from app.companies.companies import generate_ticker_enum; generate_ticker_enum()"

# Add a dependency
uv add <package>

# Database migration (Alembic)
uv run alembic upgrade head
```

## Architecture

FastAPI monolith that ingests SEC EDGAR filings and serves a Datastar-powered reactive HTML frontend.

### Data flow
```
SEC EDGAR API → edgartools → FastAPI routes → Datastar SSE → HTML browser
                                               → PostgreSQL (Alembic)
```

### Key modules

- `app/main.py` — FastAPI app with routes: `/` (root), `/updates` (SSE stream), `/latest/{ticker}/{form}`, `/{ticker}/{forms}/`
- `app/ui.py` — HTML templates rendered as f-strings with Datastar data attributes for reactivity
- `app/sec_edgar.py` — edgartools wrapper: `latest_filing_html()`, `filing_links()` for retrieving filings
- `app/db.py` — SQLAlchemy async engine with Docker secret-based password (falls back to env var)
- `app/companies/companies.py` — Fetches/caches SEC company tickers JSON (90-day TTL), generates `ticker_enum.py`
- `app/ticker_enum.py` — Auto-generated enum of 5000+ ticker → CIK mappings

### Frontend
- Datastar v1 RC7 (CDN-loaded) for reactive HTML via SSE
- Tailwind CSS v4 compiled via CLI
- No JS framework — all reactivity through `data-*` attributes and SSE patches

### Infrastructure
- Multi-stage Docker build using `uv` (python:3.13-slim-bookworm)
- PostgreSQL 17 via Docker Compose with health checks
- nginx reverse proxy in production compose
- Database password via Docker secrets (`/run/secrets/db-password`)

### Testing
- Starlette TestClient for route testing
- Tests in `app/main_test.py`
