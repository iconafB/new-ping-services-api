from fastapi import APIRouter,Depends,status,UploadFile,File,HTTPException
from crud.pings import PingsCrudClass
from schemas.pings import PingPayload,PingsPayloadResponse
from utils.auth.security import get_current_active_user_id
from utils.constants import ALLOWED_CSV_CONTENT_TYPES
pings_router=APIRouter(tags=["PINGS ROUTES"],prefix="/pings")

pings_crud=PingsCrudClass()
@pings_router.post("",status_code=status.HTTP_201_CREATED,description="Load pings as a json payload object",response_model=PingsPayloadResponse)
async def load_pings_payload(pings_payload:PingPayload,user_id=Depends(get_current_active_user_id)):
    return await pings_crud.load_pings_payload_crud(pings_payload,user_id)
#load pings
@pings_router.post("/file",status_code=status.HTTP_201_CREATED,description="Upload pings in a csv file")
async def load_file_pings(file:UploadFile=File(...,description="Upload a csv file with cell numbers to pings"),user_id=Depends(get_current_active_user_id)):
    """
        load a file with cell numbers to be pinged,file type should be as follows
        1. csv
        2. text
        3. excel
    """
    #file checking logic
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No file uploaded")
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Only csv files can be uploaded")
    if file.content_type not in ALLOWED_CSV_CONTENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid file type: {file.content_type}. Only CSV files are allowed")
    
    return

#get pings
@pings_router.get("")
async def get_pings_loaded():
    return True

#get pings status
@pings_router.get("/status")
async def check_pings_status():
    return 
    


