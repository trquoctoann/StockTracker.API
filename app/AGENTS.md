# App Source — AI Agent Instructions

> Layer-specific conventions for `app/`. Read the root `AGENTS.md` first for project-wide rules.

## Application Bootstrap

1. `setup_logging()` runs **before** any FastAPI import (ensures structlog captures all logs).
2. `create_app()` builds FastAPI instance:
   - Adds middlewares: `RequestContextMiddleware` → `AuthContextMiddleware` → `CORSMiddleware`.
   - Includes `api_v1_router` (prefix `/api`).
   - Registers global exception handlers.
   - Adds `/health` endpoint.
3. `lifespan` context manager: startup logging + graceful shutdown (dispose DB engine & Redis).

---

## Base Classes Reference

### Models (`common/base_model.py`)

| Class                    | PK Type        | Use When                               |
| ------------------------ | -------------- | -------------------------------------- |
| `BaseSQLModelWithUUID`   | `uuid.UUID`    | External IDs (e.g., Keycloak user)     |
| `BaseSQLModelWithID`     | `int` (auto)   | Internal entities (roles, tenants)     |

Both extend `AbstractAuditableSQLModel` — auto-fills `created_at/by`, `updated_at/by` from ContextVar.

### Schemas (`common/base_schema.py`)

| Class                      | Config             | Purpose                               |
| -------------------------- | ------------------ | ------------------------------------- |
| `BaseCommand`              | `extra="forbid"`   | Write DTOs — rejects unknown fields   |
| `BaseResponse`             | `extra="ignore"`   | Response DTOs — drops extra fields    |
| `PaginatedResponse[T]`     | —                  | `items`, `total`, `page`, `page_size` |
| `PaginationQueryParameter` | —                  | `limit`, `offset`, `order_by`         |
| `FilterQueryParameter`     | —                  | Operators: `eq`, `neq`, `gt`, `in_`…  |

**Subclassing rules:**
- `PaginationQueryParameter` → set `orderable_fields: ClassVar[frozenset[str] | None]`.
- `FilterQueryParameter` → set `filterable_fields: ClassVar[set[str]]`.
- Use `FilterQueryParameter.merge_ops()` to inject system filters (e.g., exclude soft-deleted).
- Use `build_query_param_dependency()` to parse query params into models.

### Repository (`common/base_repository.py`)

- `RepositoryPort[E]` (ABC) — interface: `find_all`, `count`, `exists`, `bulk_create`, `bulk_update`, `bulk_delete`.
- `SQLExecutor[M]` — concrete implementation using SQLModel session.

### Service (`common/base_service.py`)

- `QueryService[T, TFetchSpec]` — read ops: `find_by_id`, `find_all`, `find_page`, `count`, `exists`.
- `CRUDService[T]` — write ops: `create`, `update`, `delete`.

### Mapper (`common/base_mapper.py`)

- `BaseMapper[M, E]` — bidirectional Model↔Entity mapping with column cache.
- `SchemaMapper` — static utilities: `command_to_entity()`, `entity_to_response()`, `merge_source_into_target()`.

---

## Authentication & Authorization

### Dual-Token Architecture

| Token Type    | Source    | Codec                  | Principal           | Use Case                      |
| ------------- | --------- | ---------------------- | ------------------- | ----------------------------- |
| Identity      | Keycloak  | `IdentityTokenCodec`   | `IdentityPrincipal` | Initial auth, before context  |
| Context       | Internal  | `ContextTokenCodec`    | `ContextPrincipal`  | All subsequent requests       |

### Auth Guards in Routers

```python
from app.common.auth.auth_access import require_context_permissions
from app.common.auth.permission_codes import PermissionCode
from app.common.enum import RoleScope

@router.post("", status_code=201)
async def create_item(
    _auth: Annotated[
        object,
        Depends(require_context_permissions(
            PermissionCode.ITEM_CREATE,
            allowed_scopes=frozenset({RoleScope.ADMIN}),
        )),
    ],
    body: Annotated[ItemCreateRequest, Body()],
    domain_service: ItemDomainServiceDep,
) -> ResponseItem:
    ...
```

### Permission Bitmap

- All codes in `PermissionCode` (StrEnum) at `common/auth/permission_codes.py`.
- `PermissionBitmap.to_bitmap(codes)` → int.
- `has_permissions(bitmap, required_codes)` → bool (bitwise AND, O(1)).

---

## Error Handling

### Exception Hierarchy

```
AppException (base — NEVER raise directly)
├── ValidationException          422
├── UnauthorizedException        401
├── ForbiddenException           403
├── NotFoundException            404
├── BadRequestException          400
├── BusinessViolationException   400  ← Most common for domain rules
├── InternalException            500
└── ServiceUnavailableException  503
```

### Raising Errors (Pattern)

```python
# Business rule violation:
raise BusinessViolationException(
    message_key="errors.business.<module>.<error_name>",
    params={"field": value},
)

# Not found:
raise NotFoundException(
    message_key="errors.business.<module>.not_found",
    params={"id": str(id)},
)
```

### i18n Message Keys

Convention: `errors.<category>.<module>.<specific_error>`

Add to BOTH files:
- `app/i18n/errors/en.json`
- `app/i18n/errors/vi.json`

---

## Caching Patterns

### When to Cache

| ✅ DO Cache                     | ❌ DO NOT Cache          |
| ------------------------------- | ----------------------- |
| Entities fetched by ID          | Paginated list results  |
| Version numbers (token valid.)  | Filter-based queries    |
| Enrichment lookups by IDs       | Write operations        |

### Cache Pattern

```python
# Read-through:
entity = await self._cache.get_model(cache_key, EntityClass)
if entity is None:
    entity = await self._repository.find_all(...)
    if entity:
        await self._cache.set_model(cache_key, entity)

# Invalidate on write:
await self._cache.delete(cache_key)
```

### Cache Key Functions

Define in `common/cache_version_keys.py`. Pattern: `<entity>:<id>` or `<entity>:<id>:version`.

---

## Dependency Injection

### Pattern (per module)

```python
# query_dependency.py — Read path
async def get_repository(session: Annotated[AsyncSession, Depends(get_session)]) -> Repository:
    return RepositoryImpl(session)

def get_query_service(repo: Annotated[Repository, Depends(get_repository)], cache: CacheServiceDep) -> QueryService:
    return QueryService(repo, cache)

QueryServiceDep = Annotated[QueryService, Depends(get_query_service)]

# dependency.py — Write path
def get_domain_service(session, repo, query_service, cache, ...) -> DomainService:
    return DomainService(session, repo, query_service, cache, ...)

DomainServiceDep = Annotated[DomainService, Depends(get_domain_service)]
```

### Cross-Module Deps

```python
# OK — depend on QueryService across modules:
from app.modules.other.other_query_dependency import OtherQueryServiceDep

# NEVER — depend on DomainService across modules
```

---

## Coding Conventions

### Naming

| Item            | Convention                                          | Example                      |
| --------------- | --------------------------------------------------- | ---------------------------- |
| Directories     | `snake_case`                                        | `user`, `role`               |
| Files           | `snake_case`                                        | `user_domain_service.py`     |
| Classes         | `PascalCase`                                        | `UserDomainService`          |
| SQLModel tables | `PascalCase` + `Model`                              | `UserModel`                  |
| Entities        | `PascalCase` + `Entity`                             | `UserEntity`                 |
| Response DTOs   | `Response` prefix                                   | `ResponseUser`               |
| Request DTOs    | Module + `Request`                                  | `UserCreateRequest`          |
| Commands        | Action + `Command`                                  | `CreateUserCommand`          |
| Logger          | `_LOG = get_logger(__name__)`                       | Module-level constant        |
| DI aliases      | `ServiceDep = Annotated[Service, Depends(factory)]` | Type alias                   |

### Log Events

Use **UPPER_SNAKE_CASE** event names:

```python
_LOG.info("API_REQUEST_USER_CREATE", command=body)
_LOG.debug("USER_CREATING", command=command)
_LOG.debug("USER_CREATED", entity=created_entity)
```

### Router Conventions

- Prefix: `/api/<plural_resource>` (e.g., `/api/stocks`).
- Tags: `[<plural_resource>]`.
- Standard CRUD: `POST ""` (201), `PUT "/{id}"` (200), `DELETE "/{id}"` (204), `GET ""` (paginated), `GET "/all"`, `GET "/{id}"`.
- Auth param always first: `_auth: Annotated[object, Depends(require_context_permissions(...))]`.
- Body: `Annotated[RequestType, Body()]`.
- Path params: `Annotated[UUID|int, Path()]`.

### Import Organization

```python
# 1. Standard library
from __future__ import annotations
import uuid

# 2. Third-party
from fastapi import APIRouter

# 3. First-party (app.*)
from app.common.base_schema import BaseCommand
```

### Ruff Suppressions

- `B008` globally ignored (needed for `Depends()` in defaults).
- `# noqa: E402` for imports after `setup_logging()` in `main.py`.

---

## Data Flows

### Write Operation

```
HTTP Request
  → Router (auth guard, parse request DTO)
    → DomainService.create(command)
      → TransactionManager(session) {
          → validate (query_service, external checks)
          → build entity (SchemaMapper.command_to_entity)
          → repository.bulk_create([entity])
          → invalidate cache
          → return entity
        }
    → SchemaMapper.entity_to_response(entity, ResponseClass)
  → HTTP Response
```

### Read Operation

```
HTTP Request
  → Router (auth guard, parse filter/pagination)
    → QueryService.find_page(filter, pagination, fetch_spec=...)
      → repository.find_all(filter, pagination)
      → _enrich_entities(entities, fetch_spec)
      → return PaginatedResponse
    → map each entity to ResponseClass
  → HTTP Response
```

---

## New Module Checklist

When creating a new domain module (e.g., `stock`):

1. Create directory skeleton (see Module Layer Pattern in root AGENTS.md).
2. `domain/` — Entity (Pydantic) + Repository Port (ABC).
3. `infrastructure/persistence/` — SQLModel + RepositoryImpl.
4. `mapper/` — `BaseMapper[Model, Entity]`.
5. `application/query/` — FilterParameter + PaginationParameter.
6. `application/command/` — Create/Update commands.
7. `application/` — QueryService + DomainService.
8. `api/dto/` — Request/Response DTOs.
9. `api/` — Router with CRUD endpoints.
10. `*_dependency.py` + `*_query_dependency.py`.
11. Register model in `modules/models.py`.
12. Include router in `api/v1/router.py`.
13. Add i18n keys to `en.json` + `vi.json`.
14. Add permission codes to `common/auth/permission_codes.py`.
15. Create Alembic migration: `alembic revision --autogenerate -m "add <name> table"`.
