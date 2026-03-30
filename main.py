from fastapi import FastAPI,Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html,get_redoc_html
from fastapi.openapi.utils import get_openapi
from fastapi.middleware.cors import CORSMiddleware
from config.database import Base,engine
from contextlib import asynccontextmanager
from routers.credits import credits_router
from routers.auth import auth_router
from routers.pings import pings_router
from routers.clients import clients_router
from routers.health_check import health_check_router
from utils.auth.security import require_docs_auth

origin=[
    "http://localhost",
    "https://localhost:8000/docs"
]

@asynccontextmanager
async def lifespan(app:FastAPI):
    #create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    #clean on shutdown
    await engine.dispose()

app=FastAPI(title="CLIENTS PINGS API SERVICE",lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None,)
@app.get("/openapi.json",include_in_schema=False)
def openapi_json(_:bool=Depends(require_docs_auth)):
    return JSONResponse(get_openapi(title="CLIENTS PING SERVICES",version="1.0.0",routes=app.routes))

@app.get("/docs",include_in_schema=False)
def swagger_docs(_:bool=Depends(require_docs_auth)):
    return get_swagger_ui_html(openapi_url="/openapi.json",title="CLIENT PING SERVICES DOCS")


@app.get("/redoc",include_in_schema=False)
def redoc(_:bool=Depends(require_docs_auth)):
    return get_redoc_html(openapi_url="/openapi.json", title="CLIENT PING SERVICES ReDoc")

app.add_middleware(CORSMiddleware,allow_origins=origin,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.include_router(health_check_router)
app.include_router(credits_router)
app.include_router(auth_router)
app.include_router(pings_router)
app.include_router(clients_router)
