from fastapi import HTTPException,status
from models.pings import PingsInput
from schemas.pings import PingPayload,PingsCellNumber,PingsPayloadResponse
from utils.logging.logger import define_logger


pings_logger=define_logger("pings_logger","logs/pings_route.log")

class PingsCrudClass:
    #load pings payload
    async def load_pings_payload_crud(pings_payload:PingPayload,user_id:int)->PingsPayloadResponse:
        try:
            return False
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while load pings:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error occurred while loading pings")

    async def load_pings_using_a_file_upload_crud(file:str,user_id:int)->PingsPayloadResponse:
        try:
            return False
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while uploading a pings file:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading a pings file")
    

    async def check_pings_status(pings_id:str,user_id:int):
        try:
            return False
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while checking the pings status:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while checking pings status for pings_id:{pings_id} with user id:{user_id}")


    async def fetch_pings_crud(pings_id:str,user_id:int):
        try:
            return False
        except HTTPException: 
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while fetching pings for user:{user_id}:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching pinggs for user:{user_id}")