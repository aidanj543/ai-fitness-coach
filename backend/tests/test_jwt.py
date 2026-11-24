import uuid
from datetime import UTC, datetime, timedelta

import jwt
import pytest
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError, MissingRequiredClaimError

from app.core import security
from app.core.security import (
    create_access_token,
    decode_access_token,
)


def test_valid_access_token():
    user_id = str(uuid.uuid4())

    token = create_access_token(user_id)

    assert isinstance(token, str)
    assert decode_access_token(token) == user_id


def test_expired_access_token(monkeypatch):
    monkeypatch.setattr(security, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    token = create_access_token(str(uuid.uuid4()))

    with pytest.raises(ExpiredSignatureError):
        decode_access_token(token)


def test_invalid_access_token_type():
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "refresh",
        },
        security.JWT_SECRET_KEY,
        algorithm=security.JWT_ALGORITHM,
    )

    with pytest.raises(InvalidTokenError, match="Invalid access token type"):
        decode_access_token(token)


def test_missing_access_token_subject():
    token = jwt.encode(
        {
            "exp": datetime.now(UTC) + timedelta(minutes=5),
            "type": "access",
        },
        security.JWT_SECRET_KEY,
        algorithm=security.JWT_ALGORITHM,
    )

    with pytest.raises(MissingRequiredClaimError) as exc_info:
        decode_access_token(token)

    assert exc_info.value.claim == "sub"


def test_invalid_access_token_subject():
    token = create_access_token("not-a-uuid")

    with pytest.raises(InvalidTokenError, match="Access token subject must be a UUID"):
        decode_access_token(token)
