from fastapi import APIRouter,status,Query,Path,Depends
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import List
from schemas.clients import ClientsSchema,UpdateClientSchema,GetAllClientsSchema,DeleteClientSchema
from schemas.clients import CurrentClientSchema
from config.database import get_async_session
from utils.auth.security import get_current_active_user
from crud.clients import ClientsCrudClass

clients_router=APIRouter(tags=["Clients Routes"],prefix="/v1/clients")
clients_object=ClientsCrudClass()

@clients_router.get("",status_code=status.HTTP_200_OK,description="Get all clients",response_model=GetAllClientsSchema)
async def get_all_clients(session:AsyncSession=Depends(get_async_session),page:int=Query(1,description="Page Number",ge=1),page_size:int=Query(10,description="Page size",le=100),client:CurrentClientSchema=Depends(get_current_active_user)):
    return await clients_object.get_all_clients(page=page,page_size=page_size,session=session)

@clients_router.get("/active",status_code=status.HTTP_200_OK,description="Get all active clients",response_model=GetAllClientsSchema)
async def get_all_active_clients(session:AsyncSession=Depends(get_async_session),page:int=Query(1,ge=1,description="Page number"),page_size:int=Query(10,le=100,description="Provide page size number"),client:CurrentClientSchema=Depends(get_current_active_user)):
    return await clients_object.get_all_active_clients(page=page,page_size=page_size,session=session)

@clients_router.get("/{client_id}",status_code=status.HTTP_200_OK,description="Get single client by client id",response_model=ClientsSchema)
async def get_single_client(session:AsyncSession=Depends(get_async_session),client_id:int=Path(description="Provide client id"),user_id=Depends(get_current_active_user)):
    return await clients_object.get_single_client_crud(client_id=client_id,session=session)

@clients_router.patch("/delete/{client_id}",status_code=status.HTTP_202_ACCEPTED,summary="Delete client from the system",response_model=DeleteClientSchema)
async def deleted_client(session:AsyncSession=Depends(get_async_session),client_id:int=Path(description="client id"),client:CurrentClientSchema=Depends(get_current_active_user)):

    """
        Delete/Deactivate client from the system by providing the following parameters
        1. client_id this is the path parameter
    """

    return await clients_object.delete_client_soft_delete(client_id=client_id,session=session)

@clients_router.patch("/update/{client_id}",status_code=status.HTTP_202_ACCEPTED,summary="Update Client Information",response_model=ClientsSchema)
async def update_client_information(update_client:UpdateClientSchema,session:AsyncSession=Depends(get_async_session),client_id:int=Path(description="Provide client id"),client:CurrentClientSchema=Depends(get_current_active_user)):
    
    """
        Provide fields that need to be updated
        1. client name (optional)
        2. client email or username (optional)
    """
    
    return await clients_object.update_single_client(client=update_client,client_id=client_id,session=session)

