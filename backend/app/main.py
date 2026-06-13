from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.init_db import create_tables

from app.routers import (
    auth,
    products,
    categories,
    fandoms,
    cart,
    favorites,
    orders,
    artists,
    upload
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield


app = FastAPI(
    title="FanCanvas API",
    lifespan=lifespan
)


app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

app.mount(
    "/static",
    StaticFiles(directory="/app/static"),
    name="static"
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(products.router, prefix="/api/products")
app.include_router(categories.router, prefix="/api/categories")
app.include_router(fandoms.router, prefix="/api/fandoms")
app.include_router(cart.router, prefix="/api/cart")
app.include_router(favorites.router, prefix="/api/favorites")
app.include_router(orders.router, prefix="/api/orders")
app.include_router(artists.router, prefix="/api/artists")
app.include_router(upload.router, prefix="/api/upload")


@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "FanCanvas API"
    }