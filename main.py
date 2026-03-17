from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
#import routes
#setup cors
#implement routes
from routers.credits import credits_router
from routers.auth import auth_router
from routers.pings import pings_router
app=FastAPI(title="Clients pings api")
app.include_router(credits_router)
app.include_router(auth_router)
app.include_router(pings_router)
