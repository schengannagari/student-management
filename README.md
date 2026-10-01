# Student Management System

Production-grade REST API for managing students at scale (lakhs of records), built with
**FastAPI · SQLAlchemy 2.0 · SQLite (WAL) · Alembic · Pydantic v2 · JWT/RBAC**.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env              # set SMS_SECRET_KEY
alembic upgrade head              # create schema
python -m scripts.seed --admin-password 'ChangeMe!123' --students 200000   # optional load data
uvicorn app.main:app --reload     # docs: http://localhost:8000/docs
```

Login at `POST /api/v1/auth/login`, then click **Authorize** in `/docs` and paste the token.

## Architecture (strict layering — dependencies point downward only)

```
api/  (HTTP, validation, auth/RBAC)  ->  services/  (business rules, transactions)
                                     ->  repositories/  (queries only)  ->  models/ (ORM)
schemas/ = request/response contracts      core/ = config, security, logging, errors
```

| Concern | Choice |
|---|---|
| Config | `pydantic-settings`, `SMS_*` env vars, prod refuses default secret |
| DB | SQLite with WAL, `foreign_keys=ON`, busy timeout, 64 MB cache, `PRAGMA optimize` |
| Migrations | Alembic (batch mode for SQLite), deterministic constraint names |
| Integrity | Unique admission no., FKs, **optimistic locking** (`version`), **soft delete** |
| Auth | JWT + scrypt password hashes + roles (`admin`, `registrar`, `teacher`) |
| Errors | Domain exceptions -> uniform JSON `{error:{code,message,request_id}}` |
| Observability | Request-ID correlation, JSON logs, `/health/live` & `/health/ready` |
| Quality | pytest (+cov), ruff, mypy strict, GitHub Actions CI, Docker (non-root) |

## Performance (measured: 200,000 students, 2 uvicorn workers, small sandbox VM)

| Operation | Latency |
|---|---|
| Get by id | ~5 ms (≈300 req/s under 20 parallel clients) |
| List page / filter by class+status | 10–55 ms |
| Prefix search (name / admission no.) | ~30 ms (was ~200 ms before index/collation tuning) |

Design choices behind this: hard page-size cap (100), composite indexes for real query
patterns, index-friendly `LIKE 'x%'` on `NOCASE` columns, bulk inserts, `ANALYZE` after imports.

## Adding a new feature (e.g. Attendance)

1. `models/attendance.py` + import in `models/__init__.py`
2. `make migration m="add attendance"` and review the generated file
3. `schemas/`, `repositories/`, `services/`, then `api/v1/attendance.py`
4. Register the router in `api/v1/router.py`, add tests

## Important: scaling beyond SQLite

SQLite comfortably serves a school's read-heavy workload (lakhs of rows) on one server, but it
has **one writer at a time** and cannot be shared across multiple app servers. Plan to move to
**PostgreSQL** when you need: several app instances/HA, heavy concurrent writes (e.g. bulk
attendance at 9 AM), or "contains" search. The code is ready for it: only `SMS_DATABASE_URL`
changes, plus (1) replace the `NOCASE` collation with `citext`/functional index in
`models/student.py`, (2) drop the SQLite pragma hook, (3) regenerate the migration.

**Production checklist:** strong `SMS_SECRET_KEY`, HTTPS reverse proxy (nginx/Caddy), rate
limiting at the proxy, scheduled backups (`sqlite3 db ".backup file"`), change the seeded admin
password, restrict CORS origins, ship JSON logs to a central collector.

## Roadmap hooks
Attendance, fees, grades, parent portal, audit log table, FTS5 full-text search, background
jobs (Celery/RQ), refresh tokens, per-school multi-tenancy.
