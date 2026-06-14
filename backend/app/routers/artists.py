from sqlalchemy import (
    select,
    func
)

from sqlalchemy.orm import (
    selectinload
)

from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from app.database import get_db

from app.models import (
    User,
    ArtistProfile,
    Product,
    Order,
    OrderItem
)

from app.schemas import (
    ProductResponse,
    ArtistDashboardResponse
)

from app.auth import (
    get_current_artist
)

router = APIRouter(
    tags=["Artists"]
)


@router.get(
    "/profile"
)
async def artist_profile(
    current_user: User = Depends(
        get_current_artist
    ),
    db: AsyncSession = Depends(get_db)
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

    if not artist:
        raise HTTPException(
            404,
            "Artist profile not found"
        )

    return artist


@router.get(
    "/dashboard",
    response_model=ArtistDashboardResponse
)
async def dashboard(
    current_user: User = Depends(
        get_current_artist
    ),
    db: AsyncSession = Depends(get_db)
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

    if not artist:
        raise HTTPException(
            404,
            "Artist profile not found"
        )

    products_count = await db.scalar(
        select(func.count(Product.id))
        .where(Product.artist_id == artist.id)
        .where(Product.status == "active")
    )

    orders_count = await db.scalar(
        select(
            func.count(OrderItem.id)
        )
        .join(
            Product,
            Product.id ==
            OrderItem.product_id
        )
        .where(
            Product.artist_id ==
            artist.id
        )
    )

    total_sales = await db.scalar(
        select(
            func.coalesce(
                func.sum(
                    OrderItem.price *
                    OrderItem.quantity
                ),
                0
            )
        )
        .join(
            Product,
            Product.id ==
            OrderItem.product_id
        )
        .where(
            Product.artist_id ==
            artist.id
        )
    )

    return {
        "user": current_user,
        "profile": artist,
        "products_count": products_count,
        "orders_count": orders_count,
        "total_sales": float(total_sales)
    }


@router.get(
    "/products",
    response_model=list[ProductResponse]
)
async def my_products(
    current_user: User = Depends(
        get_current_artist
    ),
    db: AsyncSession = Depends(get_db)
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist),
        )
        .where(Product.artist_id == artist.id)
        .where(Product.status == "active")
        .order_by(Product.created_at.desc())
    )

    return result.scalars().unique().all()


@router.get(
    "/{artist_id}/products",
    response_model=list[ProductResponse]
)
async def artist_products(
    artist_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist),
        )
        .where(Product.artist_id == artist_id)
        .where(Product.status == "active")
    )

    return result.scalars().unique().all()


@router.get(
    "/orders"
)
async def artist_orders(
    current_user: User = Depends(
        get_current_artist
    ),
    db: AsyncSession = Depends(get_db)
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

    result = await db.execute(
        select(OrderItem)
        .join(
            Product,
            Product.id ==
            OrderItem.product_id
        )
        .where(
            Product.artist_id ==
            artist.id
        )
    )

    return result.scalars().all()