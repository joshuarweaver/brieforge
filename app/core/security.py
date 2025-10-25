"""Security utilities for API key authentication."""
import secrets
import uuid
from typing import Tuple

from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_secret(secret: str) -> str:
    """Hash a secret string."""
    return pwd_context.hash(secret)


def verify_secret(plain_secret: str, hashed_secret: str) -> bool:
    """Verify a secret string against its hashed value."""
    return pwd_context.verify(plain_secret, hashed_secret)


def generate_api_key() -> Tuple[uuid.UUID, str, str]:
    """Generate a new API key and return (key_id, plain_key, hashed_secret)."""
    key_id = uuid.uuid4()
    secret = secrets.token_urlsafe(32)
    prefix = settings.API_KEY_PREFIX.rstrip(".")
    api_key = f"{prefix}.{key_id.hex}.{secret}" if prefix else f"{key_id.hex}.{secret}"
    hashed_secret = hash_secret(secret)
    return key_id, api_key, hashed_secret


def split_api_key(api_key: str) -> Tuple[uuid.UUID, str]:
    """Split the API key into its identifier and secret components."""
    if not api_key:
        raise ValueError("Empty API key")

    parts = api_key.split(".")
    if len(parts) < 2:
        raise ValueError("Malformed API key")

    # Handle optional prefix: prefix.id.secret or id.secret
    expected_prefix = settings.API_KEY_PREFIX.rstrip(".")

    if len(parts) == 3:
        prefix, key_id_hex, secret = parts
        if expected_prefix and prefix != expected_prefix:
            raise ValueError("Invalid API key prefix")
        if not expected_prefix and prefix:
            raise ValueError("Unexpected API key prefix")
    elif len(parts) == 2:
        key_id_hex, secret = parts
        if expected_prefix:
            raise ValueError("Missing API key prefix")
    else:
        raise ValueError("Malformed API key")

    try:
        key_id = uuid.UUID(hex=key_id_hex)
    except ValueError as exc:
        raise ValueError("Invalid API key identifier") from exc

    if not secret:
        raise ValueError("Missing API key secret")

    return key_id, secret
