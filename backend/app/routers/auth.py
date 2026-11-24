from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse
)


from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User

DUMMY_PASSWORD_HASH = hash_password(
    "ThisIsADummyPasswordUsedForTimingOnly!"
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(
    payload: UserCreate,
    db: Annotated[Session, Depends(get_db)],
):

    email = str(payload.email).strip().lower()
    
    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    hashed_password = hash_password(payload.password)
    user = User(
        email=email,
        password_hash=hashed_password,
    )
    db.add(user)

    try:
        db.commit()

    except IntegrityError as exc:

        db.rollback()
        sqlstate = getattr(exc.orig, "sqlstate", None)

        constraint_name = getattr(
            getattr(exc.orig, "diag", None),
            "constraint_name",
            None,
        )

        if (
            sqlstate == "23505"
            and constraint_name == "users_email_key"
        ):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            ) from exc
        raise

    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
)
def login_user(
    payload: UserLogin,
    db: Annotated[Session, Depends(get_db)]
):
    email = str(payload.email).strip().lower()

    user = db.scalar(select(User).where(User.email == email))

    password_hash = (
    user.password_hash if user is not None
    else DUMMY_PASSWORD_HASH
    )

    password_is_valid = verify_password(
    payload.password,
    password_hash,
    )

    if not password_is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authentication": "Bearer"}
        )

    access_token = create_access_token(user_id=str(user.id))

    return TokenResponse(access_token=access_token)

