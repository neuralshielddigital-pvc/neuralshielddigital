# Alembic Migration Setup

This project uses Alembic with SQLAlchemy metadata imported from `app.core.database.Base` and model registrations in `app.models`.

## How it is wired

- `alembic.ini` provides the Alembic CLI configuration.
- `migrations/env.py` loads the application settings using `app.core.config.get_settings()`.
- The database URL is pulled from `.env` through `Settings.database_url`.
- Metadata for autogeneration comes from `Base.metadata`.

## PostgreSQL notes

- The configured dialect is `postgresql+psycopg`.
- Run migrations against the same PostgreSQL URL used by the app.
- Keep model names, indexes, foreign keys, and unique constraints in sync with the service/router layer.

## Common commands

Create a new revision from current model changes:

```bash
alembic revision --autogenerate -m "describe change"
```

Apply all migrations:

```bash
alembic upgrade head
```

Rollback one migration:

```bash
alembic downgrade -1
```

Show current revision:

```bash
alembic current
```

## Initial migration guidance

- The initial migration file in `migrations/versions/20260424_000001_initial_schema.py` is aligned to the generated SQLAlchemy models.
- If the models change before first deployment, regenerate the initial revision instead of manually drifting the schema.
- After the first production deployment, create forward-only revisions for all schema changes.
