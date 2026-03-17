from fastapi import APIRouter,Depends,status

pings_router=APIRouter(tags=["Pings Route"],prefix="/pings")
#load pings
@pings_router.post("")
async def load_file_pings():
    return
@pings_router.post("")
async def load_pings_payload():
    return

#get pings
@pings_router.get("")
async def get_pings_loaded():
    return True

#get pings status
@pings_router.get("/status")
async def check_pings_status():
    async def check_pings_status():
        return
    


