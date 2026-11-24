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

if not JWT_SECRET_KEY:
    raise RuntimeError("JWT_SECRET_KEY is missing")

try:
    secret_bytes = bytes.fromhex(JWT_SECRET_KEY)
except ValueError as exc:
    raise RuntimeError("JWT_SECRET_KEY must be hexadecimal") from exc

if len(secret_bytes) != 32:
    raise RuntimeError("JWT_SECRET_KEY must represent 32 bytes")

if ACCESS_TOKEN_EXPIRE_MINUTES <= 0:
    raise RuntimeError("Token expiration must be positive")


def create_access_token(user_id:str) -> str:

    expires_at = datetime.now(UTC)+ timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": user_id,
        "exp": expires_at,
        "type": "access"
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")

def decode_access_token(token: str)->str:

    payload = jwt.decode(
        token, JWT_SECRET_KEY, algorithms=["HS256"], options={"require": ["sub", "exp"]}
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
