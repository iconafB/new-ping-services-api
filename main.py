from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base,engine
from contextlib import asynccontextmanager
#setup cors
#implement routes
from routers.credits import credits_router
from routers.auth import auth_router
from routers.pings import pings_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    #create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #clean on shutdown
    await engine.dispose()

app=FastAPI(title="CLIENTS PINGS API SERVICE",lifespan=lifespan)
app.include_router(credits_router)
app.include_router(auth_router)
app.include_router(pings_router)
