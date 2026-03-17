from fastapi import APIRouter,Depends,status
from crud.credits import CreditsCrudClass
from schemas.credits import CreateCreditsResponse
credits_router=APIRouter(tags=["CREDITS ROUTES"],prefix="/credits")

#load credits
@credits_router.post("/load",status_code=status.HTTP_200_OK,description="Load credits",response_model=CreateCreditsResponse)
async def load_credits():
    return 
#get single history record
@credits_router.get()
async def get_single_credits_record():
    return 
#get credits history


