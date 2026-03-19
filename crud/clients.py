from fastapi import status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from datetime import timedelta
from schemas.clients import CreateClient,CreateClientResponse,LoginUser
from schemas.auth import Token
from models.clients import Clients_Table
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils.logging.logger import define_logger
from utils.auth.security import hash_password,verify_password,create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES

users_logger=define_logger("users_logger","logs/users_route.log")

"""
    implement a class that performs crud for the user entity
"""

class UsersCrudClass:
    # get all users on the system
    async def get_all_users(page:int,page_size:int,session:AsyncSession):
        try:
            return True
        except Exception as e:
            users_logger.exception(f"an internal server error occurred while fetching users:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching users")
    # get single user on the system
    async def get_single_users(user_id:int,session:AsyncSession):
        try:
            return True
        except Exception as e:
            users_logger.exception(f"an internal server error while fetching user:{user_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching user:{user_id}")
    # update user details
    async def update_users(user_id:int,session:AsyncSession):
        try:
            return True
        except Exception as e:
            users_logger.exception(f"an internal server error occurred while updating user:{user_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching user:{user_id}")
    # delete user from the system soft delete
    async def delete_user_soft_delete(user_id:int,session:AsyncSession):
        try:
            return True
        except Exception as e:
            users_logger.exception(f"an internal server error occurred while deleting user:{user_id},{str(e)}")
    # delete user from the system hard delete
    async def delete_user_hard_delete(user_id:int,session:AsyncSession):
        try:
            return True
        except Exception as e:
            users_logger.exception(f"an internal server error occurred while deleting user:{user_id},error:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while deleting user:{user_id}")

class UsersAuthCrudClass:
    #register new user
    async def register_new_client_crud(self,client:CreateClient,session:AsyncSession)->CreateClientResponse:
        print("enter the crud method and print the payload")
        print(client)
        hashed_password=hash_password(client.password)
        client_query=select(Clients_Table).where(Clients_Table.email==client.email)
        try:
            result=(await session.execute(client_query)).scalar_one_or_none()
            if result is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"an invalid credentials")
            new_client=Clients_Table(client_name=client.client_name,email=client.email,password=hashed_password)
            session.add(new_client)
            await session.commit()
            await session.refresh(new_client)
            users_logger.info(f"new cleint:{new_client.client_name},with email:{new_client.email} and client id:{new_client.client_id} registered")
            return new_client
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            users_logger.exception(f"an internal server error occurred while creating user:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error while creating a user")
    
    #login user into the system
    async def login_client_crud(self,form_data:OAuth2PasswordRequestForm,session:AsyncSession):
        user_email=form_data.username
        user_password=form_data.password
        user_query=select(Clients_Table).where(Clients_Table.email==user_email)
        try:
            result=(await session.execute(user_query)).scalar_one_or_none()
            if result is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization",headers={"WWW-Authenticate": "Bearer"})
            if not verify_password(user_password,result.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization")
            #create access token
            users_logger.info(f"user:{result.client_id} with email:{result.email} logged in")
            access_toke_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            #create access token
            token=create_access_token(data={'user_id':result.client_id},expires_delta=access_toke_expires)
            users_logger.info(f"log the token:{token}")
            #log user logged in 
            users_logger.info(f"user:{user_email} successfully logged in")
            return Token(access_token=token,token_type='Bearer')
        
        except HTTPException:
            raise

        except Exception as e:
            await session.rollback()
            users_logger.exception(f"an internal server error while login user:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while login user")



