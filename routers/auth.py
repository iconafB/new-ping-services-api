from fastapi import APIRouter,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from config.database import get_async_session
from crud.clients import UsersAuthCrudClass
from crud.admin import AdminAuthCrudClass
from schemas.clients import CreateClientResponse,CreateClient
from schemas.admin import CreateAdminResponse,CreateAdmin
from config.database import get_async_session
from sqlalchemy.ext.asyncio.session import AsyncSession
auth_router=APIRouter(tags=["AUTHENTICATION ROUTES"],prefix="/auth")
auth_service=UsersAuthCrudClass()

admin_auth_service=AdminAuthCrudClass()

@auth_router.post("/register",status_code=status.HTTP_201_CREATED,summary="Register new client",response_model=CreateClientResponse)
async def register_client(client:CreateClient,session:AsyncSession=Depends(get_async_session)):

    """
        Register a new user by providing the following fields:
        1. email
        2. password
        3. client name
        4. Ubhedeke wena!!!
    """
    
    return await auth_service.register_new_client_crud(client,session)

@auth_router.post("/login",status_code=status.HTTP_200_OK,description="Login new user into the system")
async def login_client(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],session:AsyncSession=Depends(get_async_session)):
    
    """
        Login registered users by providing the following fields
        1. email
        2. password
    """

    return await auth_service.login_client_crud(form_data,session)







