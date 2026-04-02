from __future__ import annotations

from jwcrypto.jwt import JWTExpired
from keycloak import KeycloakOpenID
from keycloak.exceptions import KeycloakAuthenticationError, KeycloakGetError
from pydantic import BaseModel, EmailStr

from app.exception.exception import InternalException, UnauthorizedException


class TokenPrincipal(BaseModel):
    subject: str
    username: str | None = None
    email: EmailStr | None = None


class KeycloakJwtDecoder:
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
    ) -> KeycloakJwtDecoder:
        openid = KeycloakOpenID(
            server_url=server_url,
            realm_name=realm_name,
            client_id=client_id,
            client_secret_key=client_secret_key,
            verify=verify,
        )
        return cls(openid)

    async def decode_access_token(self, token: str) -> TokenPrincipal:
        try:
            payload = await self._keycloak_openid.a_decode_token(token, validate=True)
        except (JWTExpired, KeycloakGetError, KeycloakAuthenticationError) as exc:
            raise UnauthorizedException(headers={"WWW-Authenticate": "Bearer"}) from exc
        except Exception as exc:
            raise InternalException(developer_message="Keycloak error: " + str(exc)) from exc

        subject = payload.get("sub")
        if not isinstance(subject, str) or not subject.strip():
            raise UnauthorizedException(headers={"WWW-Authenticate": "Bearer"})

        username = payload.get("preferred_username")
        if not isinstance(username, str):
            username = None

        email = payload.get("email")
        if not isinstance(email, str):
            email = None
        return TokenPrincipal(subject=subject, username=username, email=email)
