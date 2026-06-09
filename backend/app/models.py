from datetime import datetime
from sqlalchemy import (
    String,
    Integer,
    Boolean,
    Float,
    Date,
    DateTime,
    Text,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database import Base


# ==========================
# USERS
# ==========================

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password_hash: Mapped[str] = mapped_column(String(255))

    name: Mapped[str] = mapped_column(String(255))

    phone: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="buyer"
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    buyer_profile = relationship(
        "BuyerProfile",
        back_populates="user",
        uselist=False
    )

    artist_profile = relationship(
        "ArtistProfile",
        back_populates="user",
        uselist=False
    )

    cart_items = relationship(
        "CartItem",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    favorites = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    orders = relationship(
        "Order",
        back_populates="user"
    )


# ==========================
# BUYER PROFILE
# ==========================

class BuyerProfile(Base):
    __tablename__ = "buyer_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )

    birth_date: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True
    )

    gender: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    address: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="buyer_profile"
    )


# ==========================
# ARTIST PROFILE
# ==========================

class ArtistProfile(Base):
    __tablename__ = "artist_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True
    )

    shop_name: Mapped[str] = mapped_column(
        String(255)
    )

    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    rating: Mapped[float] = mapped_column(
        Float,
        default=5.0
    )

    available_balance: Mapped[float] = mapped_column(
        Float,
        default=0
    )

    user = relationship(
        "User",
        back_populates="artist_profile"
    )

    products = relationship(
        "Product",
        back_populates="artist"
    )


# ==========================
# CATEGORY
# ==========================

class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255),
        unique=True
    )

    products = relationship(
        "Product",
        back_populates="category"
    )


# ==========================
# FANDOM
# ==========================

class Fandom(Base):
    __tablename__ = "fandoms"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(
        String(255)
    )

    fandom_type: Mapped[str] = mapped_column(
        String(50)
    )

    products = relationship(
        "Product",
        back_populates="fandom"
    )


# ==========================
# PRODUCT
# ==========================

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)

    artist_id: Mapped[int] = mapped_column(
        ForeignKey("artist_profiles.id")
    )

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True
    )

    fandom_id: Mapped[int | None] = mapped_column(
        ForeignKey("fandoms.id"),
        nullable=True
    )

    title: Mapped[str] = mapped_column(
        String(255)
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    price: Mapped[float] = mapped_column(Float)

    stock: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    shipping_days: Mapped[int] = mapped_column(
        Integer,
        default=3
    )

    views: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    artist = relationship(
        "ArtistProfile",
        back_populates="products"
    )

    category = relationship(
        "Category",
        back_populates="products"
    )

    fandom = relationship(
        "Fandom",
        back_populates="products"
    )

    images = relationship(
        "ProductImage",
        back_populates="product",
        cascade="all, delete-orphan"
    )

    attributes = relationship(
        "ProductAttribute",
        back_populates="product",
        cascade="all, delete-orphan"
    )


# ==========================
# PRODUCT IMAGES
# ==========================

class ProductImage(Base):
    __tablename__ = "product_images"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    image_url: Mapped[str] = mapped_column(
        String(500)
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    product = relationship(
        "Product",
        back_populates="images"
    )


# ==========================
# PRODUCT ATTRIBUTES
# ==========================

class ProductAttribute(Base):
    __tablename__ = "product_attributes"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    attr_name: Mapped[str] = mapped_column(
        String(255)
    )

    attr_value: Mapped[str] = mapped_column(
        String(255)
    )

    product = relationship(
        "Product",
        back_populates="attributes"
    )


# ==========================
# CART
# ==========================

class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    user = relationship(
        "User",
        back_populates="cart_items"
    )

    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id"
        ),
    )


# ==========================
# FAVORITES
# ==========================

class Favorite(Base):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    user = relationship(
        "User",
        back_populates="favorites"
    )

    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "product_id"
        ),
    )


# ==========================
# ORDERS
# ==========================

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    total_amount: Mapped[float] = mapped_column(
        Float
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="created"
    )

    delivery_name: Mapped[str] = mapped_column(
        String(255)
    )

    delivery_address: Mapped[str] = mapped_column(
        Text
    )

    delivery_phone: Mapped[str] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user = relationship(
        "User",
        back_populates="orders"
    )

    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan"
    )


# ==========================
# ORDER ITEMS
# ==========================

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id")
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id")
    )

    quantity: Mapped[int] = mapped_column(Integer)

    price: Mapped[float] = mapped_column(Float)

    order = relationship(
        "Order",
        back_populates="items"
    )

    product = relationship("Product")