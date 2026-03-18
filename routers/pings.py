from fastapi import APIRouter,Depends,status

pings_router=APIRouter(tags=["PINGS ROUTES"],prefix="/pings")

@pings_router.post("")
async def load_pings_payload():
    return
#load pings
@pings_router.post("/file")
async def load_file_pings():
    """
        load a file with cell numbers to be pinged,file type should be as follows
        1. csv
        2. text
        3. excel
    """
    return

#get pings
@pings_router.get("")
async def get_pings_loaded():
    return True

#get pings status
@pings_router.get("/status")
async def check_pings_status():
    return 
    


