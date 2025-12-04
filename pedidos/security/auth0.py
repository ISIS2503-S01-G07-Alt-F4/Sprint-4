"""Auth0 JWT validation helpers for the Pedidos Django microservice."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from jwt import ExpiredSignatureError, InvalidTokenError, PyJWKClient, decode


class Auth0TokenError(Exception):
    """Represents an error while validating an Auth0 JWT."""

    def __init__(self, message: str, status_code: int = 401) -> None:
        super().__init__(message)
        self.status_code = status_code


class _Auth0Config:
    """Container for Auth0 configuration values."""

    def __init__(self, domain: str, audience: str, client_id: Optional[str]):
        self.domain = domain
        self.audience = audience
        self.client_id = client_id


@lru_cache
def _get_auth0_config() -> _Auth0Config:
    domain = os.getenv("AUTHZ_DOMAIN")
    audience = os.getenv("AUTHZ_AUDIENCE")
    client_id = os.getenv("CLIENT_ID")

    if not domain or not audience:
        missing = [
            name
            for name, value in (
                ("AUTHZ_DOMAIN", domain),
                ("AUTHZ_AUDIENCE", audience),
            )
            if not value
        ]
        message = "Falta configurar las variables: " + ", ".join(missing)
        raise Auth0TokenError(message, status_code=500)

    return _Auth0Config(domain=domain, audience=audience, client_id=client_id)


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    config = _get_auth0_config()
    jwks_url = f"https://{config.domain}/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def decode_auth0_token(token: str) -> dict:
    """Decodes and validates an Auth0-issued JWT, returning its payload."""

    if not token:
        raise Auth0TokenError("Token Bearer requerido", status_code=401)

    try:
        config = _get_auth0_config()
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        audience = [config.audience]
        if config.client_id and config.client_id not in audience:
            audience.append(config.client_id)

        payload = decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=audience,
            issuer=f"https://{config.domain}/",
        )
        return payload
    except Auth0TokenError:
        raise
    except ExpiredSignatureError as exc:
        raise Auth0TokenError("Token expirado", status_code=401) from exc
    except InvalidTokenError as exc:
        raise Auth0TokenError(f"Token inválido: {exc}", status_code=401) from exc
    except Exception as exc:  # pragma: no cover - defensive guardrail
        raise Auth0TokenError("No fue posible validar el token", status_code=500) from exc
