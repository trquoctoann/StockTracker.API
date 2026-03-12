# StockTracker API

A FastAPI application for tracking stocks, built with modular Clean Architecture.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLModel
- **Migration**: Alembic
- **Validation**: Pydantic
- **Linter/Formatter**: Ruff
- **Type Checking**: Pyright
- **Testing**: Pytest
- **Dependency Management**: uv
- **Pre-commit Hooks**: pre-commit
- **ASGI Server**: Uvicorn

## Project Structure

```
app/
├── core/                         # Infrastructure & cross-cutting concerns
│   ├── config.py                 #   App settings (pydantic-settings)
│   ├── database.py               #   Async engine & session
│   ├── security.py               #   JWT & password hashing
│   └── exceptions.py             #   Custom HTTP exceptions
├── common/                       # Shared base classes & utilities
│   ├── base_model.py             #   BaseModel (UUID PK + timestamps)
│   ├── base_repository.py        #   Generic CRUD repository
│   ├── base_schema.py            #   MessageResponse, PaginatedResponse[T]
│   └── pagination.py             #   Pagination helpers
├── modules/                      # Feature modules (self-contained)
│   └── user/                     #   ── User module ──
│       ├── model.py              #     Domain entity
│       ├── schemas.py            #     Request/Response DTOs
│       ├── repository.py         #     Data access layer
│       ├── service.py            #     Business logic layer
│       ├── router.py             #     API endpoints
│       └── dependencies.py       #     Module-specific DI
├── api/                          # API version aggregation
│   └── v1/
│       └── router.py             #   Includes all module routers
└── main.py                       # Application entry point

tests/
├── conftest.py                   # Shared fixtures
└── modules/
    └── user/
        └── test_user_router.py
```

## Architecture

**Modular Clean Architecture** — each module is self-contained with all layers:

```
Request → Router → Service → Repository → Database
                      ↕
                   Schemas (DTOs)
```

| Layer | File | Responsibility |
|---|---|---|
| **Presentation** | `router.py` | HTTP endpoints, request validation |
| **Business Logic** | `service.py` | Use cases, orchestration |
| **Data Access** | `repository.py` | Database queries via SQLModel |
| **Domain** | `model.py` | Entity definition |
| **DTOs** | `schemas.py` | Request/Response models |
| **DI** | `dependencies.py` | Module-scoped dependencies |

Shared infrastructure lives in `core/` and `common/`.

## Getting Started

### Prerequisites

- Python 3.12+
- PostgreSQL
- uv (`pip install uv`)

### Setup

```bash
# Create virtual environment & install dependencies
uv sync --all-extras

# Copy environment file
cp .env.example .env

# Setup pre-commit hooks
uv run pre-commit install

# Create database
createdb stocktracker

# Run migrations
uv run alembic upgrade head

# Start development server
uv run uvicorn app.main:app --reload
```

### Common Commands

```bash
# Run tests
uv run pytest

# Run linter
uv run ruff check .

# Run formatter
uv run ruff format .

# Type checking
uv run pyright

# Create new migration
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head
```

## Adding a New Module

1. Create `app/modules/<name>/` with: `model.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`, `dependencies.py`
2. Register the router in `app/api/v1/router.py`
3. Import the model in `alembic/env.py`
4. Create tests in `tests/modules/<name>/`

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
