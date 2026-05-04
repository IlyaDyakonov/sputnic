from typing import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import DB_URL


# Centralized DB engine/session factory for app and workers.
engine = create_async_engine(DB_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_maker() as session:
        yield session
