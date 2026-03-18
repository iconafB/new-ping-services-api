from fastapi import APIRouter,Depends,status,UploadFile,File,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from crud.pings import PingsCrudClass
from config.database import get_async_session
from schemas.pings import PingPayload,PingsPayloadResponse
from utils.auth.security import get_current_active_user_id
from utils.constants import ALLOWED_CSV_CONTENT_TYPES
from utils.csv_validators import validate_csv_file
pings_router=APIRouter(tags=["PINGS ROUTES"],prefix="/pings")

pings_crud=PingsCrudClass()
@pings_router.post("",status_code=status.HTTP_201_CREATED,description="Load pings as a json payload object",response_model=PingsPayloadResponse)
async def load_pings_payload(pings_payload:PingPayload,user_id=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return await pings_crud.load_pings_payload_crud(pings_payload,user_id)

#load pings
@pings_router.post("/file",status_code=status.HTTP_201_CREATED,description="Upload pings in a csv file",response_model=PingsPayloadResponse)
async def load_file_pings(file:UploadFile=File(...,description="Upload a csv file with cell numbers to pings"),user_id=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    """
        load a file with cell numbers to be pinged,file type should be as follows
        1. csv
        2. text
        3. excel
    """
    #file validation logic
    validate_csv_file(file=file)
    return await pings_crud.load_pings_using_a_file_upload_crud(file=file,user_id=user_id)

#get pings
@pings_router.get("",status_code=status.HTTP_200_OK,description="Fetch pings by providing pings_id")
async def get_pings_loaded(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return True

#get pings status
@pings_router.get("/status",status_code=status.HTTP_200_OK,description="Check the status of the pings submitted by providing the pings id")
async def check_pings_status(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return 
