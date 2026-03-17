from fastapi import APIRouter,Depends,status,Path,Query
from sqlalchemy.ext.asyncio import AsyncSession
from crud.credits import CreditsCrudClass
from schemas.credits import CreateCreditsResponse,CreateCredits,UserCreditsHistoryResponse,DeleteCreditsHistory
from utils.auth.security import get_current_active_user_id
from config.database import get_async_session
credits_router=APIRouter(tags=["CREDITS ROUTES"],prefix="/credits")
credits_object=CreditsCrudClass()

#load credits
@credits_router.post("/load",status_code=status.HTTP_201_OK,description="Load credits",response_model=CreateCreditsResponse)
async def load_credits(credits_amount:CreateCredits,user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.load_client_credits(credits_amount=credits_amount.credits_amount,user_id=user_id,session=session)

#get credits history for a user
@credits_router.get("/history",status_code=status.HTTP_200_OK,description="Get credits history for a specific user logged in")
async def get_user_credits_history(page:int,page_size:int,user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.get_all_credits_history_for_a_user(page=page,page_size=page_size,user_id=user_id,session=session)

#get single history record
@credits_router.get("/record",status_code=status.HTTP_200_OK,description="Get Single record of credits",response_model=CreateCreditsResponse)
async def get_single_credits_record(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.get_single_credits_record(user_id=user_id,session=session)

@credits_router.delete("/delete",status_code=status.HTTP_200_OK,description="Delete credit history of the current user",response_model= DeleteCreditsHistory)
async def delete_credits_history_for_current_user(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await credits_object.delete_credits_history_db(user_id=user_id,session=session)
