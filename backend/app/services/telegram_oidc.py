import base64
import time

import httpx
import jwt
from jwt import PyJWKClient

from app.config import settings

DISCOVERY_URL = "https://oauth.telegram.org/.well-known/openid-configuration"
ISSUER = "https://oauth.telegram.org"

_discovery_cache: dict | None = None
_jwks_client: PyJWKClient | None = None


async def _get_discovery_document() -> dict:
    global _discovery_cache
    if _discovery_cache is None:
        async with httpx.AsyncClient() as client:
            resp = await client.get(DISCOVERY_URL, timeout=10)
            resp.raise_for_status()
            _discovery_cache = resp.json()
    return _discovery_cache


def _get_jwks_client(jwks_uri: str) -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        _jwks_client = PyJWKClient(jwks_uri)
    return _jwks_client


async def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    """Trades the authorization code (+ PKCE verifier) for an id_token."""
    discovery = await _get_discovery_document()
    credentials = f"{settings.TELEGRAM_OIDC_CLIENT_ID}:{settings.TELEGRAM_OIDC_CLIENT_SECRET}"
    basic_auth = base64.b64encode(credentials.encode()).decode()

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            discovery["token_endpoint"],
            headers={
                "Authorization": f"Basic {basic_auth}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.TELEGRAM_OIDC_REDIRECT_URI,
                "client_id": settings.TELEGRAM_OIDC_CLIENT_ID,
                "code_verifier": code_verifier,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


async def verify_id_token(id_token: str) -> dict:
    """
    Verifies the id_token's RS256 signature against Telegram's published
    JWKS, then checks iss / aud / exp before trusting the claims inside.
    """
    discovery = await _get_discovery_document()
    jwks_client = _get_jwks_client(discovery["jwks_uri"])
    signing_key = jwks_client.get_signing_key_from_jwt(id_token)

    claims = jwt.decode(
        id_token,
        signing_key.key,
        algorithms=["RS256"],
        audience=settings.TELEGRAM_OIDC_CLIENT_ID,
        issuer=ISSUER,
    )

    if claims.get("exp", 0) < time.time():
        raise ValueError("ID token has expired")

    return claims
