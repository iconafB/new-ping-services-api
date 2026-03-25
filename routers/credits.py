from fastapi import APIRouter,Depends,status,Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from datetime import date
from crud.credits import CreditsCrudClass
from schemas.credits import CreateCreditsResponse,CreateCredits,UserCreditsHistoryResponse,DeleteCreditsHistory
from utils.auth.security import get_current_active_user_id
from config.database import get_async_session
from services.documents_downloads.credits_statements import CreditsDocuments
from crud.clients import ClientsCrudClass
credits_router=APIRouter(tags=["CREDITS SERVICE"],prefix="/credits")
credits_object=CreditsCrudClass()
current_client=ClientsCrudClass
download_services=CreditsDocuments(clients=current_client())

#load credits
@credits_router.post("/load",status_code=status.HTTP_201_CREATED,summary="Load credits",response_model=CreateCreditsResponse)
async def load_credits(credits_amount:CreateCredits,user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    """
        Top up credits for the pings service
    """
    return await credits_object.load_client_credits(credits_amount=credits_amount.credits_amount,user_id=user_id,session=session)

#get credits history for a user
@credits_router.get("/history",status_code=status.HTTP_200_OK,description="Get credits history for a specific user logged in",response_model=UserCreditsHistoryResponse)
async def get_user_credits_history(page:int=Query(1,ge=1,description="page number"),page_size:int=Query(10,le=100,description="page size"),user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.get_all_credits_history_for_a_user(page=page,page_size=page_size,user_id=user_id,session=session)

#get single history record
@credits_router.get("/record",status_code=status.HTTP_200_OK,description="Get Single record of credits",response_model=CreateCreditsResponse)
async def get_single_credits_record(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.get_single_credits_record(user_id=user_id,session=session)

@credits_router.patch("/delete",status_code=status.HTTP_200_OK,description="Delete credit history of the current user",response_model= DeleteCreditsHistory)
async def delete_credits_history_for_current_user(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.delete_credits_history_db(user_id=user_id,session=session)

@credits_router.get("/withdrawals",status_code=status.HTTP_200_OK,summary="Get all the withdrawals",response_model=UserCreditsHistoryResponse)
async def withdrawals(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session),page:int=Query(1,ge=1,description="Page Number"),page_size:int=Query(10,le=100,description="Number of items per unit page")):
    """
        Get all the credits withdrawals transactions for a client
    """
    return await credits_object.get_all_withdrawals(user_id=user_id,session=session,page=page,page_size=page_size)

@credits_router.get("/deposits",status_code=status.HTTP_200_OK,summary="Get all the depoists",response_model=UserCreditsHistoryResponse)
async def credits_deposits(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session),page:int=Query(1,ge=1,description="Page Number"),page_size:int=Query(10,le=100,description="Number of items per unit page")):
    """
        Get all the credits deposit transactions for a client
    """
    return await credits_object.get_all_deposits(user_id=user_id,session=session,page=page,page_size=page_size)

@credits_router.get("/download",status_code=status.HTTP_200_OK,summary="Download credits history",responses={200:{
    "description":"Download credits statements as PDF",
    "content":{"application/pdf":{}}
}})
async def download_credits_statements_pdf(user_id:int=Depends(get_current_active_user_id),start_date:date | None=Query(default=None,description="Filter statement from this date (inclusive). Format: YYYY-MM-DD",openapi_examples={ "month_start": {
                    "summary": "Start of month",
                    "value": "2026-03-01",
                },"financial_year_start": {
                    "summary": "Financial year start",
                    "value": "2026-01-01",
                },}),end_date:date|None=Query(default=None,description="End date for credits statements",openapi_examples={
                     "month_end": {
                    "summary": "End of month",
                    "value": "2026-03-24",
                },
                "quarter_end": {
                    "summary": "Quarter end",
                    "value": "2026-03-31",
                },
                }),session:AsyncSession=Depends(get_async_session)):
    """
        Download statemenets of credits history in pdf format
    """

    return await download_services.download_credits_pdf_statements(user_id=user_id,start_date=start_date,end_date=end_date,session=session)


