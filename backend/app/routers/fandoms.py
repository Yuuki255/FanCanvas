from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status
)

from app.database import get_db

from app.models import Fandom

from app.schemas import (
    FandomCreate,
    FandomResponse
)

from app.auth import (
    get_current_artist
)

router = APIRouter(
    tags=["Fandoms"]
)


# ==================================
# GET ALL FANDOMS
# ==================================

@router.get(
    "",
    response_model=list[FandomResponse]
)
async def get_fandoms(
    fandom_type: str | None = Query(
        default=None
    ),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Fandom)

    if fandom_type:
        stmt = stmt.where(
            Fandom.fandom_type == fandom_type
        )

    stmt = stmt.order_by(
        Fandom.name
    )

    result = await db.execute(stmt)

    return result.scalars().all()


# ==================================
# GET FANDOM
# ==================================

@router.get(
    "/{fandom_id}",
    response_model=FandomResponse
)
async def get_fandom(
    fandom_id: int,
    db: AsyncSession = Depends(get_db)
):
    fandom = await db.scalar(
        select(Fandom)
        .where(Fandom.id == fandom_id)
    )

    if not fandom:
        raise HTTPException(
            status_code=404,
            detail="Fandom not found"
        )

    return fandom


# ==================================
# CREATE FANDOM
# ==================================

@router.post(
    "",
    response_model=FandomResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_fandom(
    payload: FandomCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    fandom = Fandom(
        name=payload.name,
        fandom_type=payload.fandom_type
    )

    db.add(fandom)

    await db.commit()

    await db.refresh(fandom)

    return fandom


# ==================================
# UPDATE FANDOM
# ==================================

@router.put(
    "/{fandom_id}",
    response_model=FandomResponse
)
async def update_fandom(
    fandom_id: int,
    payload: FandomCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    fandom = await db.scalar(
        select(Fandom)
        .where(Fandom.id == fandom_id)
    )

    if not fandom:
        raise HTTPException(
            status_code=404,
            detail="Fandom not found"
        )

    fandom.name = payload.name
    fandom.fandom_type = payload.fandom_type

    await db.commit()

    await db.refresh(fandom)

    return fandom


# ==================================
# DELETE FANDOM
# ==================================

@router.delete(
    "/{fandom_id}"
)
async def delete_fandom(
    fandom_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    fandom = await db.scalar(
        select(Fandom)
        .where(Fandom.id == fandom_id)
    )

    if not fandom:
        raise HTTPException(
            status_code=404,
            detail="Fandom not found"
        )

    await db.delete(fandom)

    await db.commit()

    return {
        "message": "Fandom deleted"
    }