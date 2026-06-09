from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from app.database import get_db

from app.models import (
    CartItem,
    Product,
    User
)

from app.schemas import (
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse
)

from app.auth import get_current_user

router = APIRouter(
    tags=["Cart"]
)


@router.get(
    "",
    response_model=list[CartItemResponse]
)
async def get_cart(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
            .selectinload(Product.images),

            selectinload(CartItem.product)
            .selectinload(Product.attributes)
        )
        .where(
            CartItem.user_id == current_user.id
        )
    )

    return result.scalars().all()


@router.post(
    "",
    response_model=CartItemResponse,
    status_code=status.HTTP_201_CREATED
)
async def add_to_cart(
    payload: CartItemCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    product = await db.scalar(
        select(Product)
        .where(
            Product.id == payload.product_id
        )
    )

    if not product:
        raise HTTPException(
            404,
            "Product not found"
        )

    existing = await db.scalar(
        select(CartItem)
        .where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == payload.product_id
        )
    )

    if existing:
        existing.quantity += payload.quantity

        await db.commit()

        await db.refresh(existing)

        return existing

    item = CartItem(
        user_id=current_user.id,
        product_id=payload.product_id,
        quantity=payload.quantity
    )

    db.add(item)

    await db.commit()

    result = await db.execute(
        select(CartItem)
        .options(
            selectinload(CartItem.product)
        )
        .where(
            CartItem.id == item.id
        )
    )

    return result.scalar_one()


@router.put(
    "/{cart_item_id}",
    response_model=CartItemResponse
)
async def update_cart_item(
    cart_item_id: int,
    payload: CartItemUpdate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    item = await db.scalar(
        select(CartItem)
        .where(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id
        )
    )

    if not item:
        raise HTTPException(
            404,
            "Cart item not found"
        )

    item.quantity = payload.quantity

    await db.commit()

    await db.refresh(item)

    return item


@router.delete(
    "/{cart_item_id}"
)
async def remove_from_cart(
    cart_item_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    item = await db.scalar(
        select(CartItem)
        .where(
            CartItem.id == cart_item_id,
            CartItem.user_id == current_user.id
        )
    )

    if not item:
        raise HTTPException(
            404,
            "Cart item not found"
        )

    await db.delete(item)

    await db.commit()

    return {
        "message": "Item removed"
    }