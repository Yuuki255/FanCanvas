from datetime import date, datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional


# ==================================
# AUTH
# ==================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ==================================
# USER REGISTER
# ==================================

class UserRegister(BaseModel):
    email: EmailStr
    password: str

    name: str

    phone: Optional[str] = None

    role: str = "buyer"

    shop_name: Optional[str] = None
    bio: Optional[str] = None

    birth_date: Optional[date] = None
    gender: Optional[str] = None


# ==================================
# USER
# ==================================

class UserBase(BaseModel):
    id: int

    email: EmailStr

    name: str

    phone: Optional[str] = None

    role: str

    avatar_url: Optional[str] = None

    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ==================================
# BUYER PROFILE
# ==================================

class BuyerProfileResponse(BaseModel):
    birth_date: Optional[date] = None

    gender: Optional[str] = None

    address: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# ==================================
# ARTIST PROFILE
# ==================================

class ArtistProfileResponse(BaseModel):
    id: int

    shop_name: str

    bio: Optional[str] = None

    rating: float

    available_balance: float

    model_config = ConfigDict(from_attributes=True)


# ==================================
# USER ME
# ==================================

class UserMe(UserBase):
    buyer_profile: Optional[BuyerProfileResponse] = None

    artist_profile: Optional[ArtistProfileResponse] = None


# ==================================
# CATEGORY
# ==================================

class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: int

    name: str

    model_config = ConfigDict(from_attributes=True)


# ==================================
# FANDOM
# ==================================

class FandomCreate(BaseModel):
    name: str

    fandom_type: str


class FandomResponse(BaseModel):
    id: int

    name: str

    fandom_type: str

    model_config = ConfigDict(from_attributes=True)


# ==================================
# PRODUCT IMAGE
# ==================================

class ProductImageResponse(BaseModel):
    id: int

    image_url: str

    sort_order: int

    model_config = ConfigDict(from_attributes=True)


# ==================================
# PRODUCT ATTRIBUTE
# ==================================

class ProductAttributeCreate(BaseModel):
    attr_name: str

    attr_value: str


class ProductAttributeResponse(ProductAttributeCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)


# ==================================
# PRODUCT CREATE
# ==================================

class ProductCreate(BaseModel):
    category_id: Optional[int] = None
    fandom_id: Optional[int] = None

    title: str
    description: Optional[str] = None

    price: float
    stock: int

    shipping_days: int = 3

    attributes: list[ProductAttributeCreate] = []

    images: list[str] = []

# ==================================
# PRODUCT UPDATE
# ==================================

class ProductUpdate(BaseModel):
    category_id: Optional[int] = None

    fandom_id: Optional[int] = None

    title: Optional[str] = None

    description: Optional[str] = None

    price: Optional[float] = None

    stock: Optional[int] = None

    shipping_days: Optional[int] = None


# ==================================
# ARTIST SHORT
# ==================================

class ArtistShort(BaseModel):
    id: int

    shop_name: str

    rating: float

    model_config = ConfigDict(from_attributes=True)


# ==================================
# PRODUCT RESPONSE
# ==================================

class ProductResponse(BaseModel):
    id: int

    artist_id: int

    category_id: Optional[int]

    fandom_id: Optional[int]

    title: str

    description: Optional[str]

    price: float

    stock: int

    shipping_days: int

    views: int

    status: str

    created_at: datetime

    category: Optional[CategoryResponse] = None

    fandom: Optional[FandomResponse] = None

    images: list[ProductImageResponse] = []

    attributes: list[ProductAttributeResponse] = []

    artist: Optional[ArtistProfileResponse] = None

    model_config = ConfigDict(from_attributes=True)


# ==================================
# FAVORITES
# ==================================

class FavoriteResponse(BaseModel):
    id: int

    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


class FavoriteToggleResponse(BaseModel):
    status: str


# ==================================
# CART
# ==================================

class CartItemCreate(BaseModel):
    product_id: int

    quantity: int = 1


class CartItemUpdate(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int

    quantity: int

    product: ProductResponse

    model_config = ConfigDict(from_attributes=True)


# ==================================
# ORDER ITEMS
# ==================================

class OrderItemCreate(BaseModel):
    product_id: int

    quantity: int


class OrderItemResponse(BaseModel):
    id: int

    product_id: int

    quantity: int

    price: float

    model_config = ConfigDict(from_attributes=True)


# ==================================
# ORDER CREATE
# ==================================

class OrderCreate(BaseModel):
    items: list[OrderItemCreate]

    delivery_name: str

    delivery_address: str

    delivery_phone: str


# ==================================
# ORDER RESPONSE
# ==================================

class OrderResponse(BaseModel):
    id: int

    total_amount: float

    status: str

    delivery_name: str

    delivery_address: str

    delivery_phone: str

    created_at: datetime

    items: list[OrderItemResponse] = []

    model_config = ConfigDict(from_attributes=True)


# ==================================
# ARTIST DASHBOARD
# ==================================

class ArtistDashboardResponse(BaseModel):
    user: UserBase

    profile: ArtistProfileResponse

    products_count: int

    orders_count: int

    total_sales: float


# ==================================
# PAGINATION
# ==================================

class PaginatedProducts(BaseModel):
    total: int

    page: int

    size: int

    items: list[ProductResponse]