from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.database import get_db

from app.models import (
    Favorite,
    Product,
    User
)

from app.schemas import (
    FavoriteResponse,
    FavoriteToggleResponse
)

from app.auth import get_current_user

router = APIRouter(
    tags=["Favorites"]
)


@router.get(
    "",
    response_model=list[FavoriteResponse]
)
async def get_favorites(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Favorite)
        .options(
            selectinload(Favorite.product)
            .selectinload(Product.images),

            selectinload(Favorite.product)
            .selectinload(Product.attributes)
        )
        .where(
            Favorite.user_id ==
            current_user.id
        )
    )

    return result.scalars().all()


@router.post(
    "/{product_id}",
    response_model=FavoriteToggleResponse
)
async def toggle_favorite(
    product_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    product = await db.scalar(
        select(Product)
        .where(
            Product.id == product_id
        )
    )

    if not product:
        raise HTTPException(
            404,
            "Product not found"
        )

    favorite = await db.scalar(
        select(Favorite)
        .where(
            Favorite.user_id ==
            current_user.id,

            Favorite.product_id ==
            product_id
        )
    )

    if favorite:
        await db.delete(favorite)

        await db.commit()

        return {
            "status": "removed"
        }

    favorite = Favorite(
        user_id=current_user.id,
        product_id=product_id
    )

    db.add(favorite)

    await db.commit()

    return {
        "status": "added"
    }