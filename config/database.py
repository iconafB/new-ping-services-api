from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from settings.settings import get_settings

DATABASE_URL=f"postgresql+asyncpg://{get_settings().MASTER_DB_OWNER}:{get_settings().MASTER_DB_PASSWORD}@{get_settings().MASTER_DB_HOST_NAME}:{get_settings().MASTER_DB_PORT}/{get_settings().MASTER_DB_NAME}"

engine=create_async_engine(DATABASE_URL,echo=False,future=True,pool_timeout=30,pool_recycle=1800,pool_size=10,max_overflow=20,pre_ping=True)

async_session_maker=async_sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)

async def get_async_session()->AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

