from datetime import datetime, timedelta, UTC

from jose import JWTError, jwt

from passlib.context import CryptContext

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    Depends,
    HTTPException,
    status
)

from fastapi.security import OAuth2PasswordBearer

from app.config import settings
from app.database import get_db
from app.models import User


# ==========================================
# PASSWORD HASHING
# ==========================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return pwd_context.verify(
        plain_password,
        hashed_password
    )


# ==========================================
# JWT
# ==========================================

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login"
)


def create_access_token(
    data: dict,
    expires_delta: timedelta | None = None
):
    to_encode = data.copy()

    expire = datetime.now(UTC) + (
        expires_delta
        or timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    )

    to_encode.update(
        {
            "exp": expire
        }
    )

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


# ==========================================
# AUTHENTICATE USER
# ==========================================

async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str
):
    stmt = (
        select(User)
        .where(User.email == email)
    )

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if not user:
        return None

    if not verify_password(
        password,
        user.password_hash
    ):
        return None

    return user


# ==========================================
# GET USER BY TOKEN
# ==========================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={
            "WWW-Authenticate": "Bearer"
        }
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    stmt = (
        select(User)
        .where(User.id == int(user_id))
    )

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_exception

    return user


# ==========================================
# ACTIVE USER
# ==========================================

async def get_current_active_user(
    current_user: User = Depends(
        get_current_user
    )
):
    return current_user


# ==========================================
# ROLE CHECKS
# ==========================================

async def get_current_artist(
    current_user: User = Depends(
        get_current_user
    )
):
    if current_user.role != "artist":
        raise HTTPException(
            status_code=403,
            detail="Artist access required"
        )

    return current_user


async def get_current_buyer(
    current_user: User = Depends(
        get_current_user
    )
):
    if current_user.role != "buyer":
        raise HTTPException(
            status_code=403,
            detail="Buyer access required"
        )

    return current_user


# ==========================================
# TOKEN FACTORY
# ==========================================

def build_user_token(user: User):
    access_token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }