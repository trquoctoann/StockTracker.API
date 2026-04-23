# Tests — AI Agent Instructions

> Testing conventions for `tests/`. Read the root `AGENTS.md` first for project-wide rules.

## Test Runner

```bash
# All tests
python tests/main.py -t all

# Unit only
python tests/main.py -t unit

# Integration only
python tests/main.py -t integration

# With keyword filter
python tests/main.py -t unit -k "test_create"

# Stop at first failure
python tests/main.py -t all -x

# With coverage
python tests/main.py -t all --coverage
```

## Test Configuration

- `asyncio_mode = "auto"` — no need for `@pytest.mark.asyncio` decorator.
- Markers: `unit`, `integration`, `e2e`.
- All env vars are set in `tests/conftest.py` via `os.environ.setdefault()` before any app import.
- `REDIS_ENABLED=false` in test env — cache operations are no-ops unless using `FakeCacheService`.

---

## Directory Structure

```
tests/
├── conftest.py              ← Root: env vars + shared entity fixtures
├── main.py                  ← Unified pytest runner CLI
├── support/
│   ├── factories.py         ← make_user(), make_role(), make_tenant(), etc.
│   └── fakes.py             ← FakeIdentityProvider, FakeUserRoleRepository, FakeCacheService
├── unit/
│   ├── test_base_schema.py
│   ├── test_cache_version_keys.py
│   ├── test_context_token_codec.py
│   ├── test_enums.py
│   ├── test_exceptions.py
│   ├── test_i18n_catalog.py
│   ├── test_middleware.py
│   ├── test_password_validation.py
│   ├── test_permission_bitmap.py
│   ├── test_principals.py
│   ├── test_schema_mapper.py
│   └── test_services/      ← Domain service unit tests
│       ├── test_user_domain_service.py
│       ├── test_role_domain_service.py
│       ├── test_tenant_domain_service.py
│       └── test_account_domain_service.py
└── integration/
    ├── conftest.py          ← app_client fixture + dependency overrides
    ├── test_health.py
    ├── test_auth_middleware.py
    ├── test_error_handling.py
    ├── test_user_endpoints.py
    ├── test_role_endpoints.py
    ├── test_tenant_endpoints.py
    └── test_account_endpoints.py
```

---

## Factories (`support/factories.py`)

Use factory functions to create test entities with sensible defaults:

| Function                       | Returns              | Key Defaults                                    |
| ------------------------------ | -------------------- | ----------------------------------------------- |
| `make_user(**kw)`              | `UserEntity`         | `DEFAULT_USER_ID`, `username="testuser"`         |
| `make_user_role(**kw)`         | `UserRoleEntity`     | `scope=ADMIN`, `role_ids=[1]`                    |
| `make_role(**kw)`              | `RoleEntity`         | `id=1`, `scope=ADMIN`, `type=CUSTOM`             |
| `make_tenant(**kw)`            | `TenantEntity`       | `id=1`, `path="1."`                              |
| `make_permission(**kw)`        | `PermissionEntity`   | `id=1`, `code="USER_READ"`                       |
| `make_context_principal(**kw)` | `ContextPrincipal`   | All permissions bitmap, `scope=ADMIN`             |
| `make_identity_principal(**kw)`| `IdentityPrincipal`  | `username="testuser"`                             |

**Always** use factories instead of constructing entities manually.

---

## Fakes (`support/fakes.py`)

| Class                     | What It Replaces        | Behavior                                      |
| ------------------------- | ----------------------- | --------------------------------------------- |
| `FakeIdentityProvider`    | Keycloak adapter        | Returns fixed UUID, all mutations are no-ops   |
| `FakeUserRoleRepository`  | UserRoleRepository      | In-memory list with full CRUD                  |
| `FakeCacheService`        | Redis CacheService      | In-memory dict, `_use_redis()` always True     |

### Mock Session Helper

```python
from tests.support.fakes import make_mock_async_session

session = make_mock_async_session()
# Properly mocks in_transaction(), begin(), begin_nested()
```

---

## Unit Test Pattern

Unit tests verify **pure business logic** with mocked dependencies.

```python
import pytest
from unittest.mock import AsyncMock
from tests.support.factories import make_user
from tests.support.fakes import make_mock_async_session

@pytest.fixture()
def session():
    return make_mock_async_session()

@pytest.fixture()
def user_repo():
    return AsyncMock()

@pytest.fixture()
def query_service():
    return AsyncMock()

@pytest.fixture()
def cache():
    return AsyncMock()

@pytest.fixture()
def service(session, user_repo, query_service, cache):
    return UserDomainService(session=session, user_repository=user_repo, ...)

class TestCreate:
    async def test_success(self, service, user_repo, query_service):
        query_service.username_exists.return_value = False
        user_repo.bulk_create.return_value = [make_user()]
        result = await service.create(CreateUserCommand(...))
        assert result.username == "testuser"

    async def test_duplicate_raises(self, service, query_service):
        query_service.username_exists.return_value = True
        with pytest.raises(BusinessViolationException):
            await service.create(...)
```

### Rules

- Test class per operation: `TestCreate`, `TestUpdate`, `TestDelete`.
- Happy path + every distinct error path.
- Use `AsyncMock()` for repositories and query services.
- Use `make_mock_async_session()` for the DB session.
- Assert return values AND side effects (e.g., `user_repo.bulk_create.assert_called_once()`).

---

## Integration Test Pattern

Integration tests verify the **HTTP layer** with dependency overrides.

### The `app_client` Fixture

Located in `tests/integration/conftest.py`:

1. Pre-populates `FakeCacheService` with version entries for token validation.
2. Creates app via `create_app()`.
3. Overrides **ALL** dependencies with mocks/fakes via `app.dependency_overrides`.
4. Uses `httpx.AsyncClient` + `ASGITransport`.

### Test Examples

```python
class TestCreateEndpoint:
    async def test_create_201(self, app_client, admin_auth_header, mock_service):
        mock_service.create.return_value = make_user()
        resp = await app_client.post("/api/users", json={...}, headers=admin_auth_header)
        assert resp.status_code == 201

    async def test_no_auth_401(self, app_client):
        resp = await app_client.post("/api/users", json={...})
        assert resp.status_code == 401

    async def test_forbidden_403(self, app_client):
        # Use a token with insufficient permissions
        token = _build_context_token(permissions_bitmap=0)
        resp = await app_client.post("/api/users", json={...}, headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 403
```

### Dependency Override Pattern

```python
app.dependency_overrides[get_session] = lambda: mock_session
app.dependency_overrides[get_cache_service] = lambda: fake_cache
app.dependency_overrides[get_<module>_repository] = lambda: mock_repository
app.dependency_overrides[get_<module>_query_service] = lambda: mock_query_service
app.dependency_overrides[get_<module>_domain_service] = lambda: mock_domain_service
```

- Override at the **factory function** level (not the type).
- Use `lambda:` to return the mock instance.
- Overrides are cleared after test: `app.dependency_overrides.clear()`.

---

## Adding Tests for a New Module

### Step 1: Factory

Add to `support/factories.py`:

```python
def make_<entity>(**kw) -> <Entity>Entity:
    return <Entity>Entity(
        id=kw.get("id", 1),
        # ... sensible defaults ...
        created_at=_NOW,
        created_by="system",
        updated_at=_NOW,
        updated_by="system",
    )
```

### Step 2: Unit Tests

Create `tests/unit/test_services/test_<module>_domain_service.py`:
- Fixture: construct service with mocked deps.
- Test class per operation (Create, Update, Delete).
- Cover happy path + each business rule violation.

### Step 3: Integration Tests

1. Add mock fixtures to `tests/integration/conftest.py`:
   ```python
   @pytest.fixture()
   def mock_<module>_repository():
       return AsyncMock()

   @pytest.fixture()
   def mock_<module>_domain_service():
       return AsyncMock(spec=<Module>DomainService)
   ```

2. Add overrides to `app_client` fixture:
   ```python
   app.dependency_overrides[get_<module>_repository] = lambda: mock_<module>_repository
   app.dependency_overrides[get_<module>_domain_service] = lambda: mock_<module>_domain_service
   ```

3. Create `tests/integration/test_<module>_endpoints.py`:
   - Test each CRUD endpoint: 201, 200, 204.
   - Test auth: 401 (no token), 403 (wrong permissions).
   - Test validation: 422 (invalid body).

---

## Assertion Checklist

- [ ] Status code matches expected.
- [ ] Response body structure matches `ResponseXxx` schema.
- [ ] Service method called with correct arguments.
- [ ] Auth guard rejects unauthenticated requests (401).
- [ ] Auth guard rejects unauthorized requests (403).
- [ ] Validation errors return 422 with field details.
- [ ] Business violations return 400 with i18n message.
