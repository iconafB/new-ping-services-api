from fastapi import HTTPException,status,UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.pings import PingsInput,pinged_input
from schemas.pings import PingPayload,PingsCellNumber,PingsPayloadResponse,LoadPingPayloadResponse
from utils.logging.logger import define_logger
from crud.credits import CreditsCrudClass
from services.cell_number_validations.cell_number_validation import validate_sa_cell_numbers
from services.pings.pings import bulk_insert_pings_input

pings_logger=define_logger("pings_logger","logs/pings_route.log")
credits_object=CreditsCrudClass()
class PingsCrudClass:
    #one credit per single ping
    #load pings payload
    async def load_pings_payload_crud(self,pings:PingPayload,user_id:int,session:AsyncSession)->PingsPayloadResponse:
        try:
            # before loading pings, check if the credits balance matches
            credits_record=await credits_object.get_single_credits_record(user_id=user_id,session=session)
            credits=credits_record.credits_total
            pings_length=len(pings.cell_numbers)
            if credits==0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"insufficient credits balance:{credits} for user:{user_id} to process the requested pings payload")
            # validate the cell numbers an clean the cell numbers
            validated_cell_numbers=validate_sa_cell_numbers(pings.cell_numbers)
            invalid_count=validated_cell_numbers["invalid_count"]
            valid_numbers=validated_cell_numbers["valid_numbers"]
            valid_count=validated_cell_numbers["valid_count"]
            # one ping per unit credit
            number_of_records=len(valid_numbers)
            updated_details=await credits_object.update_remaining_credits_balance(number_of_records=number_of_records,user_id=user_id,session=session)
            # send the pings to the pings service to the dedago service
            # input the pings into a table locally
            pinges_loaded_to_db=await bulk_insert_pings_input(session=session,cell_numbers=valid_numbers,user_id=user_id)
            print("print the loading response location")
            print(pinges_loaded_to_db)
            # commit these numbers to a database table
            pings_logger.info(f"valid count cell numbers:{valid_count}, and invalid count:{invalid_count}")
            return LoadPingPayloadResponse(valid_numbers_count=valid_count,invalid_number_count=invalid_count,pinged_cell_numbers=valid_numbers,remaining_credits=updated_details.remaining_credits)
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while load pings:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error occurred while loading pings")

    async def load_pings_using_a_file_upload_crud(self,file:UploadFile,user_id:int,session:AsyncSession)->PingsPayloadResponse:
        try:
            
            return True
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while uploading a pings file:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading a pings file")
    

    async def check_pings_status(self,pings_id:str,user_id:int,session:AsyncSession):
       
        try:
           return
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while checking the pings status:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while checking pings status for pings_id:{pings_id} with user id:{user_id}")


    async def fetch_pings_crud(self,pings_id:str,user_id:int,session:AsyncSession):
        try:
            return False
        except HTTPException: 
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while fetching pings for user:{user_id}:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching pinggs for user:{user_id}")
    
    async def test_pings(self,session:AsyncSession):
        stmt=select(pinged_input).limit(5)
        try:
            result_query=await session.execute(stmt)
            return result_query.all()
        
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")
        

