from fastapi import status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from datetime import timedelta
from schemas.users import CreateUser,CreateUserResponse,LoginUser
from schemas.auth import Token
from models.users import Users
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
    async def register_new_user_crud(user:CreateUser,session:AsyncSession)->CreateUserResponse:
        hashed_password=hash_password(user.password)
        user_query=select(Users).where(Users.email==user.email)
        try:
            result=(await session.execute(user_query)).scalar_one_or_none()
            if result is not None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"user already exists")
            new_user=Users(first_name=user.first_name,last_name=user.last_name,password=hashed_password,email=user.email)
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)
            users_logger.info(f"user:{user.email} registered")
            return new_user
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            users_logger.exception(f"an internal server error occurred while creating user:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error while creating a user")
    
    #login user into the system
    async def login_user_crud(form_data:OAuth2PasswordRequestForm,session:AsyncSession):
        user_email=form_data.username
        user_password=form_data.password
        user_query=select(Users).where(Users.email==user_email)
        try:
            result=(await session.execute(user_query)).scalar_one_or_none()
            if result is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization",headers={"WWW-Authenticate": "Bearer"})
            if not verify_password(user_password,result.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization")
            #create access token
            users_logger.info(f"user:{result.id} with email:{result.email} logged in")
            access_toke_expires=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            #create access token
            token=create_access_token(data={'user_id':result.id},expires_delta=access_toke_expires)
            #log user logged in 
            users_logger.info(f"user:{user_email} successfully logged in")
            return Token(token=token,token_type='Bearer')
        except HTTPException:
            raise
        except Exception as e:
            users_logger.exception(f"an internal server error while login user:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while login user")

