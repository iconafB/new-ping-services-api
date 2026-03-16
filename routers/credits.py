from fastapi import APIRouter

credits_router=APIRouter(tags=["CREDITS ROUTES"],prefix="/credits")
@credits_router.post()
async def load_credits():
    return True

