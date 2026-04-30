# StockTracker API — AI Agent Instructions

> **Source of Truth** for all AI coding agents (Gemini, Copilot, Claude Code, Cursor, Cline).
> Subdirectory-level files in `app/` and `tests/` provide domain-specific context.

## Project Identity

| Field           | Value                                          |
| --------------- | ---------------------------------------------- |
| Framework       | **FastAPI** (ASGI, async throughout)            |
| ORM             | **SQLModel** (Pydantic v2 + SQLAlchemy 2.x)    |
| Database        | **PostgreSQL** via `asyncpg`                    |
| Migrations      | **Alembic** (auto-generate from model registry) |
| Auth (IdP)      | **Keycloak** (OIDC) + internal context tokens   |
| Cache           | **Redis** (optional, circuit-breaker protected)  |
| Message Queue   | **RabbitMQ** via `aio-pika` (topic exchange)     |
| Logging         | **structlog** (JSON in prod, colorama in dev)    |
| Python          | `>= 3.12`                                       |
| Package Manager | **uv** (lockfile: `uv.lock`)                    |
| Linting         | **ruff** (line-length 120) + **pyright** (basic) |
| Testing         | **pytest** + `pytest-asyncio` + **httpx**        |

## Architecture at a Glance

```
app/
├── api/v1/router.py        ← Router aggregation (prefix /api)
├── common/                 ← Shared base classes, auth, cache, consumers, enums
├── core/                   ← Singletons: config, database, redis, rabbitmq, logger
├── exception/              ← Exception hierarchy + global handlers
├── i18n/                   ← Error message catalogs (en.json, vi.json)
├── middleware/             ← ASGI middlewares (request context, auth)
├── modules/                ← Domain modules (DDD-lite)
│   ├── user/  role/  tenant/  permission/  account/
│   └── models.py           ← SQLModel registry for Alembic
└── main.py                 ← App factory (create_app)

tests/
├── conftest.py             ← Env vars + shared fixtures
├── main.py                 ← Unified runner: python tests/main.py [-t unit|integration|all]
├── support/                ← factories.py, fakes.py
├── unit/                   ← Pure-logic tests (no I/O)
└── integration/            ← HTTP endpoint tests with stubbed deps
```

## Critical Rules (ALWAYS Follow)

1. **Async everything** — All DB, cache, and IdP operations MUST be `async`.
2. **Never modify `setup_logging()` ordering** — It must run before FastAPI imports in `main.py`.
3. **Register new SQLModel tables** in `app/modules/models.py` for Alembic discovery.
4. **Add env vars** to both `app/core/config.py` (Settings class) AND `.env.example`.
5. **Line length** max **120 characters** (ruff enforced).
6. **Use `extra="forbid"`** in all `BaseCommand` subclasses; `extra="ignore"` in `BaseResponse`.
7. **Wrap all write operations** in `TransactionManager(self._session)`.
8. **Soft delete** — Set `record_status = RecordStatus.DELETED`, never physical delete.
9. **i18n both locales** — Add error messages to BOTH `en.json` and `vi.json`.
10. **Cross-module deps** — Only depend on `QueryService` across modules, never `DomainService`.
11. **Standardized exceptions only** — NEVER raise raw Python exceptions (`ValueError`, `RuntimeError`, `Exception`, etc.). Always use the pre-defined hierarchy in `app/exception/exception.py` (`InternalException`, `ServiceUnavailableException`, `BusinessViolationException`, etc.). Add i18n keys to both `en.json` and `vi.json` when creating new error messages.
12. **Alembic Migrations** — Whenever you create a new module with new database models, you MUST automatically generate Alembic migrations not using alembic command like (`alembic revision --autogenerate -m "add <module_name> tables"`), but create it yourself following the structure of the other migration files after registering the models in `models.py`. **IMPORTANT**: You must create a separate migration file for each individual module, do not bundle multiple modules into a single migration file.
13. **Permission** - It should be created automatically when creating a new module and applying to routers.
14. **Many-to-Many Updates** — When updating a many-to-many relationship (e.g., assigning stocks to an index, or industries to a stock), NEVER delete all existing records and recreate them. Always compute the delta (current vs. new), explicitly delete ONLY the missing records, and create ONLY the newly added records.
15. **Comprehensive Testing** — Whenever a new module is created or an existing module is updated, you MUST implement all necessary unit and integration tests to ensure the functionality works as expected.

## Commands

| Action             | Command                                              |
| ------------------ | ---------------------------------------------------- |
| Run dev server     | `uvicorn app.main:app --reload`                      |
| Run all tests      | `python tests/main.py -t all`                        |
| Run unit tests     | `python tests/main.py -t unit`                       |
| Run integration    | `python tests/main.py -t integration`                |
| Lint               | `ruff check .`                                       |
| Format             | `ruff format .`                                      |
| Type check         | `pyright`                                            |
| New migration      | `alembic revision --autogenerate -m "description"`   |
| Apply migrations   | `alembic upgrade head`                               |
| Install deps       | `uv sync`                                            |
| Install dev deps   | `uv sync --extra dev`                                |

## Guardrails (NEVER Do)

- **Never** hardcode secrets — use environment variables via `Settings`.
- **Never** import from `infrastructure/` in `domain/` layer — direction is inward only.
- **Never** modify `.env` directly — update `.env.example` as template.
- **Never** use `print()` — use `_LOG = get_logger(__name__)` with structlog.
- **Never** add raw SQL without going through `SQLExecutor`.
- **Never** create synchronous DB/cache/HTTP operations.
- **Never** raise raw Python exceptions (`ValueError`, `RuntimeError`, `TypeError`, `Exception`) — use `app/exception/exception.py` hierarchy.

## Module Layer Pattern (DDD-Lite)

Each domain module follows this exact structure:

```
modules/<name>/
├── api/                      ← HTTP layer (thin controllers)
│   ├── dto/                  ← Request/Response DTOs
│   └── <name>_router.py
├── application/              ← Business logic
│   ├── command/              ← Write DTOs (BaseCommand)
│   ├── query/                ← Filter & Pagination params
│   ├── <name>_domain_service.py   ← Write ops (CRUDService)
│   └── <name>_query_service.py    ← Read ops (QueryService)
├── domain/                   ← Pure business models
│   ├── <name>_entity.py      ← Pydantic entity (NO SQLAlchemy)
│   └── <name>_repository.py  ← Abstract port (ABC)
├── infrastructure/           ← Implementations
│   └── persistence/
│       ├── <name>_model.py        ← SQLModel(table=True)
│       └── <name>_repository_impl.py
├── mapper/
│   └── <name>_mapper.py      ← BaseMapper[Model, Entity]
├── <name>_dependency.py       ← DomainService DI wiring
└── <name>_query_dependency.py ← QueryService DI wiring
```

## Cross-Tool Compatibility

This file is the **single source of truth**. If your tool uses a different filename:

| Tool              | Expected File                              | Action                |
| ----------------- | ------------------------------------------ | --------------------- |
| Gemini / Jules    | `AGENTS.md`                                | ✅ This file           |
| Claude Code       | `CLAUDE.md`                                | Symlink → `AGENTS.md` |
| Cursor            | `.cursorrules`                             | Symlink → `AGENTS.md` |

See subdirectory `AGENTS.md` files for layer-specific instructions:
- [`app/AGENTS.md`](app/AGENTS.md) — Application source code conventions
- [`tests/AGENTS.md`](tests/AGENTS.md) — Testing patterns and conventions
