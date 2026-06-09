from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.database import get_db

from app.models import Category

from app.schemas import (
    CategoryCreate,
    CategoryResponse
)

from app.auth import (
    get_current_artist
)

router = APIRouter(
    tags=["Categories"]
)


# ==================================
# GET ALL CATEGORIES
# ==================================

@router.get(
    "",
    response_model=list[CategoryResponse]
)
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Category)
        .order_by(Category.name)
    )

    return result.scalars().all()


# ==================================
# GET CATEGORY
# ==================================

@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    category = await db.scalar(
        select(Category)
        .where(Category.id == category_id)
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    return category


# ==================================
# CREATE CATEGORY
# ==================================

@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    exists = await db.scalar(
        select(Category)
        .where(Category.name == payload.name)
    )

    if exists:
        raise HTTPException(
            status_code=400,
            detail="Category already exists"
        )

    category = Category(
        name=payload.name
    )

    db.add(category)

    await db.commit()

    await db.refresh(category)

    return category


# ==================================
# UPDATE CATEGORY
# ==================================

@router.put(
    "/{category_id}",
    response_model=CategoryResponse
)
async def update_category(
    category_id: int,
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    category = await db.scalar(
        select(Category)
        .where(Category.id == category_id)
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    category.name = payload.name

    await db.commit()

    await db.refresh(category)

    return category


# ==================================
# DELETE CATEGORY
# ==================================

@router.delete(
    "/{category_id}"
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_artist)
):
    category = await db.scalar(
        select(Category)
        .where(Category.id == category_id)
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found"
        )

    await db.delete(category)

    await db.commit()

    return {
        "message": "Category deleted"
    }