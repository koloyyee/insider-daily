# Dev Notes

## Alembic (DB migrations)

### Init (one-time)
```sh
uv run alembic init alembic
```
Creates `alembic/` directory with `env.py`, `script.py.mako`, and `alembic.ini`.

After init, edit `alembic.ini` (sqlalchemy.url) and `alembic/env.py` (point `target_metadata` at your `Base.metadata`).

### Create a migration
```sh
uv run alembic revision --autogenerate -m "description of change"
```
Scans your SQLAlchemy models vs the current DB state and generates a migration script in `alembic/versions/`.

### Apply migrations
```sh
uv run alembic upgrade head
```

### Rollback one step
```sh
uv run alembic downgrade -1
```

### Check status
```sh
uv run alembic current
uv run alembic history
```

## Notes

- `uv run` uses the project's virtualenv managed by `uv` — no need to `pip install` or activate a venv manually.
- All Docker commands use `docker compose` (v2), not `docker-compose`.
- DB password comes from Docker secrets (`/run/secrets/db-password`) inside containers, or env var `DB_PASSWORD` locally.
- DB host defaults to `localhost` for local dev, overridden to `db` inside Docker via the `DB_HOST` env var in compose.yaml.
