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
    User,
    Product,
    Order,
    OrderItem,
    CartItem
)

from app.schemas import (
    OrderCreate,
    OrderResponse
)

from app.auth import get_current_user

router = APIRouter(
    tags=["Orders"]
)


@router.get(
    "",
    response_model=list[OrderResponse]
)
async def get_orders(
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
        )
        .where(
            Order.user_id == current_user.id
        )
        .order_by(
            Order.created_at.desc()
        )
    )

    return result.scalars().unique().all()


@router.get(
    "/{order_id}",
    response_model=OrderResponse
)
async def get_order(
    order_id: int,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
        )
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )

    order = result.scalar_one_or_none()

    if not order:
        raise HTTPException(
            404,
            "Order not found"
        )

    return order


@router.post(
    "",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    payload: OrderCreate,
    current_user: User = Depends(
        get_current_user
    ),
    db: AsyncSession = Depends(get_db)
):
    total_amount = 0
    order_items = []

    for item in payload.items:

        product = await db.scalar(
            select(Product)
            .where(
                Product.id == item.product_id
            )
        )

        if not product:
            raise HTTPException(
                404,
                f"Product {item.product_id} not found"
            )

        if product.stock < item.quantity:
            raise HTTPException(
                400,
                f"Insufficient stock for {product.title}"
            )

        line_total = (
            product.price *
            item.quantity
        )

        total_amount += line_total

        order_items.append(
            {
                "product": product,
                "quantity": item.quantity
            }
        )

    order = Order(
        user_id=current_user.id,
        total_amount=total_amount,
        delivery_name=payload.delivery_name,
        delivery_address=payload.delivery_address,
        delivery_phone=payload.delivery_phone,
        status="created"
    )

    db.add(order)

    await db.flush()

    for item in order_items:

        product = item["product"]

        product.stock -= item["quantity"]

        db.add(
            OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item["quantity"],
                price=product.price
            )
        )

    cart_items = await db.execute(
        select(CartItem)
        .where(
            CartItem.user_id ==
            current_user.id
        )
    )

    for cart_item in cart_items.scalars():
        await db.delete(cart_item)

    await db.commit()

    result = await db.execute(
        select(Order)
        .options(
            selectinload(Order.items)
        )
        .where(
            Order.id == order.id
        )
    )

    return result.scalar_one()