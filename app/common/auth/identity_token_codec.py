from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Annotated

from fastapi import Depends
from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError

from app.common.auth.principals import IdentityPrincipal
from app.core.config import settings
from app.exception.exception import IdentityTokenUnauthorizedException, InternalException


class IdentityTokenCodec(ABC):
    @abstractmethod
    async def decode(self, token: str) -> IdentityPrincipal:
        pass


class KeycloakCodec(IdentityTokenCodec):
    def __init__(self, keycloak_openid: KeycloakOpenID) -> None:
        self._keycloak_openid = keycloak_openid

    @classmethod
    def build(
        cls,
        *,
        server_url: str,
        realm_name: str,
        client_id: str,
        client_secret_key: str | None,
        verify: bool,
    ) -> KeycloakCodec:
        openid = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret_key,
            verify=verify,
        )
        return cls(openid)

    async def decode(self, token: str) -> IdentityPrincipal:
        try:
            payload = await self._keycloak_openid.a_decode_token(token, validate=True)
        except (JWTExpired, KeycloakGetError, KeycloakAuthenticationError) as exc:
            raise IdentityTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc
        except Exception as exc:
            raise InternalException(developer_message="Keycloak error: " + str(exc)) from exc

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise IdentityTokenUnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        username = payload.get("preferred_username")
        if not isinstance(username, str):
            username = None

        email = payload.get("email")
        if not isinstance(email, str):
            email = None
        return IdentityPrincipal(subject=subject, username=username, email=email)


def get_identity_token_codec() -> IdentityTokenCodec:
    return KeycloakCodec.build(
        server_url=settings.OIDC_KEYCLOAK_SERVER_URL,
        realm_name=settings.OIDC_KEYCLOAK_REALM,
        client_id=settings.OIDC_KEYCLOAK_CLIENT_ID,
        client_secret_key=settings.OIDC_KEYCLOAK_CLIENT_SECRET,
        verify=settings.OIDC_KEYCLOAK_VERIFY_TLS,
    )


IdentityTokenCodecDep = Annotated[IdentityTokenCodec, Depends(get_identity_token_codec)]
