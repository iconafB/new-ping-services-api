from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase
from settings.settings import get_settings

class Base(DeclarativeBase):
    pass

database_url=URL.create(drivername="postgresql+asyncpg",username=get_settings().TEST_DB_USERNAME,password=get_settings().TEST_DB_PASSWORD,host=get_settings().TEST_DB_HOST_NAME,port=get_settings().TEST_DB_PORT,database=get_settings().TEST_DB_NAME)
engine=create_async_engine(database_url,echo=False,future=True,pool_timeout=30,pool_recycle=1800,pool_size=10,max_overflow=20,pool_pre_ping=True)
async_session_maker=async_sessionmaker(bind=engine,expire_on_commit=False,class_=AsyncSession)
async def get_async_session()->AsyncGenerator[AsyncSession,None]:
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()

