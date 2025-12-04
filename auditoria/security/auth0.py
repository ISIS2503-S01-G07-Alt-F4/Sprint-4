"""Auth0 JWT validation helpers for the Inventario microservice."""
from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient, decode
from jwt import ExpiredSignatureError, InvalidTokenError


class _Auth0Config:
    """
    Contiene la configuración necesaria para validar tokens de Auth0.
    """

    def __init__(self, domain: str, audience: str, client_id: Optional[str]):
        self.domain = domain
        self.audience = audience
        self.client_id = client_id


bearer_scheme = HTTPBearer(auto_error=False)


@lru_cache
def _get_auth0_config() -> _Auth0Config:
    domain = os.getenv("AUTHZ_DOMAIN")
    audience = os.getenv("AUTHZ_AUDIENCE")
    client_id = os.getenv("CLIENT_ID")

    if not domain or not audience:
        raise RuntimeError("AUTHZ_DOMAIN and AUTHZ_AUDIENCE environment variables are required for Auth0 validation")

    return _Auth0Config(domain=domain, audience=audience, client_id=client_id)


@lru_cache
def _get_jwks_client() -> PyJWKClient:
    config = _get_auth0_config()
    jwks_url = f"https://{config.domain}/.well-known/jwks.json"
    return PyJWKClient(jwks_url)


def validate_auth0_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """
    Valida un token JWT de Auth0 y retorna el payload decodificado.
    Lanza HTTPException si la validación falla.
    
    """

    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Bearer requerido")

    token = credentials.credentials

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
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(exc),
        ) from exc
    except ExpiredSignatureError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado") from exc
    except InvalidTokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Token inválido: {exc}") from exc
    except Exception as exc: 
        print(exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No fue posible validar el token",
        ) from exc
    
