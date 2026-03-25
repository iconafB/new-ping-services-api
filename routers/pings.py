from fastapi import APIRouter,Depends,status,UploadFile,File,Query
from sqlalchemy.ext.asyncio.session import AsyncSession
from crud.pings import PingsCrudClass
from config.database import get_async_session
from schemas.pings import PingPayload,PingsPayloadResponse,LoadPingPayloadResponse,PingsOverview
from utils.auth.security import get_current_active_user_id
from utils.file_helpers.csv_validators import validate_csv_files
pings_router=APIRouter(tags=["PINGS ROUTES"],prefix="/pings")
pings_crud=PingsCrudClass()
#,response_model=PingsPayloadResponse
@pings_router.post("",status_code=status.HTTP_201_CREATED,summary="Load pings as a json payload object",response_model=LoadPingPayloadResponse)
async def load_pings_payload(pings:PingPayload,user_id=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    """
        Please note that duplicate cell numbers will be filtered out and not sent to the ping machine
    """
    return await pings_crud.load_pings_payload_crud(pings=pings,user_id=user_id,session=session)


#load pings
@pings_router.post("/file",status_code=status.HTTP_201_CREATED,description="Upload file with cell numbers to ping",response_model=LoadPingPayloadResponse)
async def load_file_with_pings(file:UploadFile=File(...,description="Upload a csv file with cell numbers to pings"),user_id=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):

    """
        load a file with cell numbers to be pinged,file type should be as follows
        (i) csv
    """
    
    csv_file=await validate_csv_files(file=file)
    return await pings_crud.load_pings_using_a_file_upload_crud(file=csv_file,user_id=user_id,session=session)



#get pings
@pings_router.get("",status_code=status.HTTP_200_OK,description="Fetch pings by providing pings_id")
async def get_pings_loaded(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return True

#get pings status
@pings_router.get("/status",status_code=status.HTTP_200_OK,description="Check the status of the pings submitted by providing the pings id")
async def check_pings_status(user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    return 

#pings overview router
@pings_router.get("/overview",status_code=status.HTTP_200_OK,summary="get the total pings sent per client",response_model=PingsOverview)
async def get_pings_overview(page:int=Query(1,ge=1,description="Page Number"),page_size:int=Query(10,le=100,description="Total number of items per unit page"),user_id:int=Depends(get_current_active_user_id),session:AsyncSession=Depends(get_async_session)):
    """
        Get the total pings overviews for the logged in client

    """
    return await pings_crud.get_pings_overview(page=page,page_size=page_size,user_id=user_id,session=session)