# StockTracker API

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

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
