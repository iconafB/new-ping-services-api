from fastapi import APIRouter,status

clients_router=APIRouter(tags=["Clients Routes"],prefix="/clients")

@clients_router.post("",status_code=status.HTTP_201_CREATED,description="Create a new client")
async def create_new_client():
    return True

@clients_router.get("",status_code=status.HTTP_200_OK,description="Get all clients")
async def get_all_clients():
    return True
