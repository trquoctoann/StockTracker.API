from __future__ import annotations

import uuid

from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.base_mapper import SchemaMapper
from app.common.base_service import CRUDService
from app.common.enum import RecordStatus, RoleScope, UserStatus
from app.core.logger import get_logger
from app.core.transaction_manager import TransactionManager
from app.exception.exception import BusinessViolationException
from app.modules.role.application.role_query_service import RoleQueryService
from app.modules.tenant.application.tenant_query_service import TenantQueryService
from app.modules.user.application.command.user_command import CreateUserCommand, SetUserRolesCommand, UpdateUserCommand
from app.modules.user.application.user_query_service import UserFetchSpec, UserQueryService
from app.modules.user.domain.identity_provider import (
    IdentityCreateUserPayload,
    IdentityProvider,
    IdentityUpdatePasswordPayload,
    IdentityUpdateProfilePayload,
)
from app.modules.user.domain.user_entity import UserEntity
from app.modules.user.domain.user_repository import UserRepository, UserRoleRepository

logger = get_logger(__name__)


class UserDomainService(CRUDService[UserEntity]):
    def __init__(
        self,
        session: AsyncSession,
        user_repository: UserRepository,
        user_role_repository: UserRoleRepository,
        query_service: UserQueryService,
        tenant_query_service: TenantQueryService,
        role_query_service: RoleQueryService,
        identity_provider: IdentityProvider,
    ) -> None:
        self._session = session
        self._user_repository = user_repository
        self._user_role_repository = user_role_repository
        self._query_service = query_service
        self._tenant_query_service = tenant_query_service
        self._role_query_service = role_query_service
        self._identity_provider = identity_provider

    async def create(self, command: CreateUserCommand) -> UserEntity:
        async with TransactionManager(self._session):
            logger.debug("USER_CREATING", command=command)

            await self.validate_command(command)
            identity_user_id = await self._identity_provider.create_user(
                IdentityCreateUserPayload(
                    username=command.username,
                    email=command.email,
                    first_name=command.first_name,
                    last_name=command.last_name,
                    password=command.password,
                )
            )
            try:
                keycloak_uuid = uuid.UUID(identity_user_id)
            except ValueError as exc:
                raise BusinessViolationException(message_key="errors.business.user.identity_invalid_id") from exc

            entity = SchemaMapper.command_to_entity(
                command,
                UserEntity,
                overrides={
                    "id": keycloak_uuid,
                    "status": UserStatus.ACTIVE,
                    "record_status": RecordStatus.ENABLED,
                    "version": 1,
                },
            )

            created = await self._user_repository.bulk_create([entity])
            created_entity = created[0]

            logger.debug("USER_CREATED", entity=created_entity)
            return created_entity

    async def update(self, command: UpdateUserCommand) -> UserEntity:
        async with TransactionManager(self._session):
            logger.debug("USER_UPDATING", command=command)

            existing = await self._query_service.get_by_id(command.id)

            await self.validate_command(command, existing)
            await self._identity_provider.update_profile(
                IdentityUpdateProfilePayload(
                    identity_user_id=str(existing.id),
                    first_name=command.first_name,
                    last_name=command.last_name,
                )
            )

            updating = SchemaMapper.merge_source_into_target(
                command,
                existing,
                forbidden=frozenset[str](
                    {
                        "id",
                        "username",
                        "email",
                        "status",
                        "record_status",
                        "version",
                        "created_at",
                        "created_by",
                        "updated_at",
                        "updated_by",
                    }
                ),
            )

            saved = await self._user_repository.bulk_update([updating])
            saved_entity = saved[0]

            logger.debug("USER_UPDATED", entity=saved_entity)
            return saved_entity

    async def set_roles(self, command: SetUserRolesCommand) -> UserEntity:
        async with TransactionManager(self._session):
            logger.debug("USER_SET_ROLES", command=command)

            user = await self._query_service.get_by_id(command.id)

            expected_scope = RoleScope.ADMIN
            if command.tenant_id is not None:
                await self._tenant_query_service.get_by_id(command.tenant_id)
                expected_scope = RoleScope.TENANT

            role_ids = set(command.role_ids)
            if role_ids:
                roles = await self._role_query_service.find_all_by_ids(list(role_ids))
                found_ids = {r.id for r in roles if r.id is not None}
                missing = role_ids - found_ids
                if missing:
                    raise BusinessViolationException(
                        message_key="errors.business.role.not_found",
                        params={"id": ", ".join(str(x) for x in sorted(missing))},
                    )

                invalid_scope_ids = [r.id for r in roles if r.id is not None and r.scope != expected_scope]
                if invalid_scope_ids:
                    raise BusinessViolationException(
                        message_key="errors.business.user.role_scope_mismatch",
                        params={
                            "expected_scope": expected_scope.value,
                            "role_ids": ", ".join(str(x) for x in sorted(invalid_scope_ids)),
                        },
                    )

            await self._user_role_repository.upsert_user_roles(
                user_id=user.id,
                scope=expected_scope,
                tenant_id=command.tenant_id,
                role_ids=role_ids,
            )
            return await self._query_service.get_by_id(user.id, fetch_spec=UserFetchSpec(user_roles=True))

    async def update_profile(
        self,
        user_id: uuid.UUID,
        *,
        first_name: str,
        last_name: str | None,
    ) -> UserEntity:
        async with TransactionManager(self._session):
            existing = await self._query_service.get_by_id(user_id)

            existing.first_name = first_name
            existing.last_name = last_name

            await self._identity_provider.update_profile(
                IdentityUpdateProfilePayload(
                    identity_user_id=str(existing.id),
                    first_name=first_name,
                    last_name=last_name,
                )
            )

            saved = await self._user_repository.bulk_update([existing])
            return saved[0]

    async def update_password(self, user_id: uuid.UUID, *, new_password: str) -> None:
        async with TransactionManager(self._session):
            user = await self._query_service.get_by_id(user_id)
            await self._identity_provider.update_password(
                IdentityUpdatePasswordPayload(identity_user_id=str(user.id), new_password=new_password, temporary=False)
            )

    async def delete(self, user_id: uuid.UUID) -> None:
        async with TransactionManager(self._session):
            logger.debug("USER_DELETING", id=user_id)

            existing = await self._query_service.get_by_id(user_id)
            await self._identity_provider.delete_user(str(existing.id))

            if existing.record_status != RecordStatus.DELETED:
                existing.record_status = RecordStatus.DELETED
                existing.version += 1
            await self._user_repository.bulk_update([existing])

            logger.debug("USER_DELETED", id=user_id)

    async def validate_command(
        self,
        command: CreateUserCommand | UpdateUserCommand,
        existing: UserEntity | None = None,
    ) -> None:
        if isinstance(command, UpdateUserCommand):
            pass
        else:
            await self._validate_user_uniqueness(command.username, command.email)

    async def _validate_user_uniqueness(
        self,
        username: str,
        email: str,
        existing: UserEntity | None = None,
        user_id: uuid.UUID | None = None,
    ) -> None:
        if (existing is None or existing.username != username) and await self._query_service.username_exists(
            username, exclude_id=user_id
        ):
            raise BusinessViolationException(
                message_key="errors.business.user.username_taken", params={"username": username}
            )

        if (existing is None or existing.email != email) and await self._query_service.email_exists(
            email, exclude_id=user_id
        ):
            raise BusinessViolationException(message_key="errors.business.user.email_taken", params={"email": email})
