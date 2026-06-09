from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.database import get_db

from app.models import (
    User,
    BuyerProfile,
    ArtistProfile
)

from app.schemas import (
    UserRegister,
    LoginRequest,
    Token,
    UserMe
)

from app.auth import (
    hash_password,
    authenticate_user,
    build_user_token,
    get_current_user
)

router = APIRouter(
    tags=["Authentication"]
)


# ==========================================
# REGISTER
# ==========================================

@router.post(
    "/register",
    response_model=Token,
    status_code=status.HTTP_201_CREATED
)
async def register(
    payload: UserRegister,
    db: AsyncSession = Depends(get_db)
):
    existing_user = await db.scalar(
        select(User)
        .where(User.email == payload.email)
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    user = User(
        email=payload.email,
        password_hash=hash_password(
            payload.password
        ),
        name=payload.name,
        phone=payload.phone,
        role=payload.role
    )

    db.add(user)

    await db.flush()

    if payload.role == "artist":
        artist_profile = ArtistProfile(
            user_id=user.id,
            shop_name=payload.shop_name
            or payload.name,
            bio=payload.bio
        )

        db.add(artist_profile)

    else:
        buyer_profile = BuyerProfile(
            user_id=user.id,
            birth_date=payload.birth_date,
            gender=payload.gender
        )

        db.add(buyer_profile)

    await db.commit()

    await db.refresh(user)

    return build_user_token(user)


# ==========================================
# LOGIN
# ==========================================

@router.post(
    "/login",
    response_model=Token
)
async def login(
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(
        db=db,
        email=payload.email,
        password=payload.password
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    return build_user_token(user)


# ==========================================
# CURRENT USER
# ==========================================

@router.get(
    "/me",
    response_model=UserMe
)
async def me(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(User)
        .options(
            selectinload(
                User.buyer_profile
            ),
            selectinload(
                User.artist_profile
            )
        )
        .where(
            User.id == current_user.id
        )
    )

    result = await db.execute(stmt)

    user = result.scalar_one()

    return user


# ==========================================
# REFRESH USER DATA
# ==========================================

@router.get(
    "/profile",
    response_model=UserMe
)
async def profile(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(User)
        .options(
            selectinload(
                User.buyer_profile
            ),
            selectinload(
                User.artist_profile
            )
        )
        .where(
            User.id == current_user.id
        )
    )

    result = await db.execute(stmt)

    return result.scalar_one()