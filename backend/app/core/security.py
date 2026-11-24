import os
from datetime import datetime, UTC, timedelta
from pathlib import Path
from uuid import UUID

import jwt
from dotenv import load_dotenv
from jwt.exceptions import InvalidTokenError

from pwdlib import PasswordHash

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if (
    not JWT_SECRET_KEY
    or len(JWT_SECRET_KEY.strip().encode("utf-8")) < 32
    or JWT_SECRET_KEY.strip() == "replace_with_random_64_character_hex_secret"
):
    raise ValueError("JWT_SECRET_KEY must be set to a secret of at least 32 bytes")

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be positive")

def create_access_token(user_id:str) -> str:

    expires_at = datetime.now(UTC)+ timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
        "type": "access"
    }

    return jwt.encode(payload)

def decode_access_token(token: str)->str:

    payload = jwt.decode(
        token, JWT_SECRET_KEY, algorithms=["HS256"], options={"require": ["exp"]}
    )

    if payload.get("type") != "access":
        raise InvalidTokenError("Invalid access token type")
    subject = payload.get("sub")

    if not isinstance(subject, str):
        raise InvalidTokenError("Access token subject must be a UUID")
    try:
        UUID(subject)
    except ValueError as exc:
        raise InvalidTokenError("Access token subject must be a UUID") from exc
    return subject

password_hash = PasswordHash.recommended()

def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)
