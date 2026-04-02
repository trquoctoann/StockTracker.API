from __future__ import annotations

from keycloak import KeycloakAdmin, KeycloakOpenIDConnection
from keycloak.exceptions import KeycloakOperationError

from app.exception.exception import (
    BusinessViolationException,
    InternalException,
    UnauthorizedException,
)
from app.modules.user.domain.identity_provider import (
    IdentityCreateUserPayload,
    IdentityProvider,
    IdentityUpdatePasswordPayload,
    IdentityUpdateProfilePayload,
)


class KeycloakIdentityProvider(IdentityProvider):
    def __init__(self, keycloak_admin: KeycloakAdmin) -> None:
        self._keycloak_admin = keycloak_admin

    @classmethod
    def build(
        cls,
        *,
        server_url: str,
        realm_name: str,
        username: str,
        password: str,
        client_id: str,
        client_secret_key: str | None,
        verify: bool,
    ) -> KeycloakIdentityProvider:
        connection = KeycloakOpenIDConnection(
            server_url=server_url,
            realm_name=realm_name,
            user_realm_name=realm_name,
            username=username,
            password=password,
            client_id=client_id,
            client_secret_key=client_secret_key,
            verify=verify,
        )
        return cls(KeycloakAdmin(connection=connection))

    async def create_user(self, payload: IdentityCreateUserPayload) -> str:
        try:
            user_id = await self._keycloak_admin.a_create_user(
                {
                    "username": payload.username,
                    "email": str(payload.email),
                    "firstName": payload.first_name,
                    "lastName": payload.last_name or "",
                    "credentials": [{"value": payload.password, "type": "password", "temporary": False}],
                    "enabled": True,
                },
                exist_ok=False,
            )
        except KeycloakOperationError as exc:
            self._map_keycloak_error(exc)
            raise
        return str(user_id)

    async def update_profile(self, payload: IdentityUpdateProfilePayload) -> None:
        data = {
            "firstName": payload.first_name,
            "lastName": payload.last_name or "",
        }
        try:
            await self._keycloak_admin.a_update_user(user_id=payload.identity_user_id, payload=data)
        except KeycloakOperationError as exc:
            self._map_keycloak_error(exc)
            raise

    async def update_password(self, payload: IdentityUpdatePasswordPayload) -> None:
        try:
            await self._keycloak_admin.a_set_user_password(
                user_id=payload.identity_user_id,
                password=payload.new_password,
                temporary=payload.temporary,
            )
        except KeycloakOperationError as exc:
            self._map_keycloak_error(exc)
            raise

    async def delete_user(self, identity_user_id: str) -> None:
        try:
            await self._keycloak_admin.a_delete_user(user_id=identity_user_id)
        except KeycloakOperationError as exc:
            self._map_keycloak_error(exc)
            raise

    @staticmethod
    def _map_keycloak_error(exc: KeycloakOperationError) -> None:
        status_code = getattr(exc, "response_code", None)
        if status_code == 401:
            raise UnauthorizedException() from exc
        if status_code == 403:
            raise InternalException(
                developer_message="Keycloak error: Something wrong with role settings of superadmin"
            ) from exc
        if status_code == 409:
            raise BusinessViolationException(message_key="errors.business.user.identity_conflict")
        if status_code == 404:
            raise BusinessViolationException(message_key="errors.business.user.identity_not_found")
        raise InternalException(developer_message="Keycloak error: " + str(exc)) from exc
