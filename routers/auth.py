from fastapi import APIRouter,status,Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from sqlalchemy.ext.asyncio.session import AsyncSession
from config.database import get_async_session
from crud.clients import UsersAuthCrudClass
from crud.admin import AdminAuthCrudClass
from schemas.clients import CreateClientResponse,CreateClient
from config.database import get_async_session
from sqlalchemy.ext.asyncio.session import AsyncSession
auth_router=APIRouter(tags=["AUTHENTICATION ROUTES"],prefix="/auth")
auth_service=UsersAuthCrudClass()

@auth_router.post("/register",status_code=status.HTTP_201_CREATED,description="Register new client",response_model=CreateClientResponse)
async def register_client(client:CreateClient,session:AsyncSession=Depends(get_async_session)):
    """
        Register a new user by providing the following fields:
        1. email
        2. password
        3. client name
    """
    return await auth_service.register_new_client_crud(client,session)

@auth_router.post("/login",status_code=status.HTTP_200_OK,description="Login new user into the system")
async def login_client(form_data:Annotated[OAuth2PasswordRequestForm,Depends()],session:AsyncSession=Depends(get_async_session)):
    """
        login registered users by providing the following fields
        1. email
        2. password
    """
    print("enter login method")
    return await auth_service.login_client_crud(form_data,session)

@auth_router.post("/admin/register")

async def register_new_admin():
    """
    register admin by providing the following fields
    1. email/username
    2. password
    3. first name
    4. last name
    5. is_admin
    """
    return True



@auth_router.post("/admin/login")
async def login_admin():
    """
        login the admin using the following fields
        1. password 
        2. email
    """
    return True

