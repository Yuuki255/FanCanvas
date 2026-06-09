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
    HTTPException,
    Query,
    status
)

from app.database import get_db

from app.models import (
    Product,
    ProductAttribute,
    ArtistProfile,
    User
)

from app.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    PaginatedProducts
)

from app.auth import (
    get_current_artist
)

router = APIRouter(
    tags=["Products"]
)


# =====================================
# CREATE PRODUCT
# =====================================

@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    payload: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_artist
    )
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

    product = Product(
        artist_id=artist.id,
        category_id=payload.category_id,
        fandom_id=payload.fandom_id,
        title=payload.title,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        shipping_days=payload.shipping_days
    )

    db.add(product)

    await db.flush()

    for attr in payload.attributes:
        db.add(
            ProductAttribute(
                product_id=product.id,
                attr_name=attr.attr_name,
                attr_value=attr.attr_value
            )
        )

    await db.commit()

    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist)
        )
        .where(Product.id == product.id)
    )

    return result.scalar_one()


# =====================================
# PRODUCT LIST
# =====================================

@router.get(
    "",
    response_model=PaginatedProducts
)
async def get_products(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),

    category_id: int | None = None,
    fandom_id: int | None = None,

    min_price: float | None = None,
    max_price: float | None = None,

    in_stock: bool | None = None,

    search: str | None = None,

    sort: str = "newest",

    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist)
        )
    )

    count_stmt = select(
        func.count(Product.id)
    )

    if category_id:
        stmt = stmt.where(
            Product.category_id == category_id
        )

        count_stmt = count_stmt.where(
            Product.category_id == category_id
        )

    if fandom_id:
        stmt = stmt.where(
            Product.fandom_id == fandom_id
        )

        count_stmt = count_stmt.where(
            Product.fandom_id == fandom_id
        )

    if min_price is not None:
        stmt = stmt.where(
            Product.price >= min_price
        )

        count_stmt = count_stmt.where(
            Product.price >= min_price
        )

    if max_price is not None:
        stmt = stmt.where(
            Product.price <= max_price
        )

        count_stmt = count_stmt.where(
            Product.price <= max_price
        )

    if in_stock:
        stmt = stmt.where(
            Product.stock > 0
        )

        count_stmt = count_stmt.where(
            Product.stock > 0
        )

    if search:
        stmt = stmt.where(
            Product.title.ilike(
                f"%{search}%"
            )
        )

        count_stmt = count_stmt.where(
            Product.title.ilike(
                f"%{search}%"
            )
        )

    if sort == "price_asc":
        stmt = stmt.order_by(
            Product.price.asc()
        )

    elif sort == "price_desc":
        stmt = stmt.order_by(
            Product.price.desc()
        )

    elif sort == "popular":
        stmt = stmt.order_by(
            Product.views.desc()
        )

    else:
        stmt = stmt.order_by(
            Product.created_at.desc()
        )

    total = (
        await db.execute(count_stmt)
    ).scalar()

    stmt = stmt.offset(
        (page - 1) * size
    ).limit(size)

    result = await db.execute(stmt)

    products = result.scalars().unique().all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": products
    }


# =====================================
# PRODUCT DETAIL
# =====================================

@router.get(
    "/{product_id}",
    response_model=ProductResponse
)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist)
        )
        .where(
            Product.id == product_id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            404,
            "Product not found"
        )

    product.views += 1

    await db.commit()

    return product


# =====================================
# UPDATE PRODUCT
# =====================================

@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
async def update_product(
    product_id: int,
    payload: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_artist
    )
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

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

    if product.artist_id != artist.id:
        raise HTTPException(
            403,
            "Access denied"
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(
            product,
            field,
            value
        )

    await db.commit()

    result = await db.execute(
        select(Product)
        .options(
            selectinload(Product.images),
            selectinload(Product.attributes),
            selectinload(Product.category),
            selectinload(Product.fandom),
            selectinload(Product.artist)
        )
        .where(
            Product.id == product_id
        )
    )

    return result.scalar_one()


# =====================================
# DELETE PRODUCT
# =====================================

@router.delete(
    "/{product_id}"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(
        get_current_artist
    )
):
    artist = await db.scalar(
        select(ArtistProfile)
        .where(
            ArtistProfile.user_id ==
            current_user.id
        )
    )

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

    if product.artist_id != artist.id:
        raise HTTPException(
            403,
            "Access denied"
        )

    await db.delete(product)

    await db.commit()

    return {
        "message": "Product deleted"
    }