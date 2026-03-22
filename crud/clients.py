from fastapi import status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select,func
from datetime import timedelta
from math import ceil
from schemas.clients import CreateClient,CreateClientResponse
from schemas.auth import Token
from schemas.clients import GetAllClientsSchema,ClientsSchema,UpdateClientSchema,DeleteClientSchema,AllClientsSchema
from models.clients import Clients_Table
from sqlalchemy.ext.asyncio.session import AsyncSession
from utils.logging.logger import define_logger
from utils.auth.security import hash_password,verify_password,create_access_token,ACCESS_TOKEN_EXPIRE_MINUTES

users_logger=define_logger("users_logger","logs/users_route.log")

"""
    implement a class that performs crud for the user entity
"""

class ClientsCrudClass:
    # get all users on the system
    async def get_all_clients(self,page:int,page_size:int,session:AsyncSession):
        try:
            offset=(page - 1)*page_size
            base_query=select(Clients_Table)
            count_query=select(func.count(Clients_Table.client_id))
            base_query=(base_query.order_by(Clients_Table.created_at.desc()).offset(offset).limit(page_size))
            total_records_query=await session.execute(count_query)
            total_records=total_records_query.scalar_one()
            clients_results=await session.execute(base_query)
            clients=clients_results.scalars().all()
            total_pages=ceil(total_records/page_size) if total_records >0 else 1
            return GetAllClientsSchema(total=total_records,page=page,page_size=page_size,results=[AllClientsSchema.model_validate(client) for client in clients])
        except HTTPException:
            raise
        except Exception as e:
            users_logger.exception(f"an internal server error occurred while fetching users:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching users")
    #get active users
    async def get_all_active_clients(self,page:int,page_size:int,session:AsyncSession):
        try:
            offset=(page - 1)*page_size
            base_query=select(Clients_Table)
            count_query=select(func.count(Clients_Table.client_id))
            base_query=(base_query.where(Clients_Table.is_active==True).order_by(Clients_Table.created_at.desc()).offset(offset).limit(page_size))
            total_records_query=await session.execute(count_query)
            total_records=total_records_query.scalar_one()
            clients_results=await session.execute(base_query)
            clients=clients_results.scalars().all()
            total_pages=ceil(total_records/page_size) if total_records >0 else 1
            return GetAllClientsSchema(total=total_records,page=page,page_size=page_size,results=[AllClientsSchema.model_validate(client) for client in clients])
        except HTTPException:
            raise

        except Exception as e:
            users_logger.exception(f"an internal server error occurred while fetching users:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching users")
        
    # get single user on the system
    async def get_single_client_crud(self,client_id:int,session:AsyncSession):
        client_query=select(Clients_Table).where(Clients_Table.client_id==client_id)
        try:
            client_query_result=await session.execute(client_query)
            client=client_query_result.scalar_one_or_none()
            if client is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"client:{client_id} does not exist")
            if client.is_active is False:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"client:{client_id} is not active, contact administrator for activation")
            return ClientsSchema(client_id=client.client_id,client_email=client.email,created_at=client.created_at,is_active=client.is_active)
        except HTTPException:
            raise

        except Exception as e:
            users_logger.exception(f"an internal server error while fetching user:{client_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching user:{client_id}")
    # update user details
    async def update_single_client(self,client:UpdateClientSchema,client_id:int,session:AsyncSession)->ClientsSchema:
        client_query=select(Clients_Table).where(Clients_Table.client_id==client_id)
        try:
            client_query_result=await session.execute(client_query)
            result=client_query_result.scalar_one_or_none()
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"client with client_id:{client_id} does not exist")
            if client.client_email is not None:
                result.email=client.client_email
            if client.client_name is not None:
                result.client_name=client.client_name
            await session.commit()
            await session.refresh(result)
            return ClientsSchema(client_id=result.client_id,client_email=result.email,created_at=result.created_at,is_active=True)
        except HTTPException:
            raise

        except Exception as e:
            users_logger.exception(f"an internal server error occurred while updating user:{client_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching user:{client_id}")
        
    # delete user from the system soft delete
    async def delete_client_soft_delete(self,client_id:int,session:AsyncSession):
        client_query=select(Clients_Table).where(Clients_Table.client_id==client_id)
        try:
            client_query_result=await session.execute(client_query)
            client_result=client_query_result.scalar_one_or_none()
            if client_result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"client with client id:{client_id} does not exist")
            client_result.is_active=False
            await session.commit()
            await session.refresh(client_result)
            users_logger.info(f"client:{client_id} has been deleted")
            return DeleteClientSchema(message=f"Client with client id:{client_id} has been deactivated")
        except HTTPException:
            raise

        except Exception as e:
            users_logger.exception(f"an internal server error occurred while deleting user:{client_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while deleting a client with client id:{client_id}")
        
    # delete user from the system hard delete
    async def delete_client_hard_delete(self,client_id:int,session:AsyncSession)->DeleteClientSchema:
        client_query=select(Clients_Table).where(Clients_Table.client_id==client_id)
        try:
            client_query_result=await session.execute(client_query)
            client_result=client_query_result.first()
            if client_result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"client:{client_id} does not exist")
            await session.delete(client_result)
            await session.commit()
            return DeleteClientSchema(message=f"Client with client id:{client_id} has been deleted")
        except HTTPException:
            raise

        except Exception as e:
            users_logger.exception(f"an internal server error occurred while deleting user:{client_id},error:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while deleting user:{client_id}")

class UsersAuthCrudClass:
    #register new user
    async def register_new_client_crud(self,client:CreateClient,session:AsyncSession)->CreateClientResponse:
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

