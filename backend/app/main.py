from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.config import get_settings
from app.database import engine
from app.models.base import Base

# Import all models so they are registered with Base.metadata before create_all
import app.models.user
import app.models.listing
import app.models.broker
import app.models.wishlist
import app.models.token_blacklist
import app.models.notification

from app.auth.router import router as auth_router
from app.routers.users import router as users_router
from app.routers.listings import router as listings_router
from app.routers.brokers import router as brokers_router
from app.routers.wishlist import router as wishlist_router
from app.routers.chat import router as chat_router
from app.routers.admin import router as admin_router
from app.routers.notifications import router as notifications_router

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-create tables on startup (simple alternative to Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description="Backend API for the Real Estate property listing platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Session middleware for OAuth state
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(listings_router)
app.include_router(brokers_router)
app.include_router(wishlist_router)
app.include_router(chat_router)
app.include_router(admin_router)
app.include_router(notifications_router)


@app.get("/", tags=["Health"])
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
