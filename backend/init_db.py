import asyncio
from app.database import engine
from app.models.base import Base

import app.models.user
import app.models.listing
import app.models.broker
import app.models.wishlist
import app.models.token_blacklist

from sqlalchemy import text

async def init_models():
    async with engine.begin() as conn:
        print("Creating tables...")
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(init_models())
