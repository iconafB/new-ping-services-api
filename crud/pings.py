from fastapi import HTTPException,status,UploadFile
from sqlalchemy import select,func
from math import ceil
import polars as pl
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.pings import pinged_input,ClientPingsOverview
from schemas.pings import PingPayload,PingsPayloadResponse,LoadPingPayloadResponse,PingOverview,PingsOverview
from utils.logging.logger import define_logger
from utils.auth.client_tokens import generate_secure_token,hash_token
from crud.credits import CreditsCrudClass
from services.cell_number_validations.cell_number_validation import validate_sa_cell_numbers
from services.pings.pings import bulk_insert_pings_input
from services.files_services.csv_services import CSVClass
pings_logger=define_logger("pings_logger","logs/pings_route.log")
credits_object=CreditsCrudClass()
class PingsCrudClass:
    #one credit per single ping
    #load pings payload
    def __init__(self):
        #this is tight coupling,needs to be resolved
        self.csv_service=CSVClass()
    #charge them even for submitting wrong data, we don't clean for free

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
            pings_loaded_to_db=await bulk_insert_pings_input(session=session,cell_numbers=valid_numbers,user_id=user_id)
            # commit these numbers to a database table
            pings_logger.info(f"valid count cell numbers:{valid_count}, and invalid count:{invalid_count}")
            return LoadPingPayloadResponse(valid_numbers_count=valid_count,invalid_number_count=invalid_count,remaining_credits=updated_details.remaining_credits)
        

        except HTTPException:
            raise

        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while load pings:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error occurred while loading pings")

    async def load_pings_using_a_file_upload_crud(self,file:UploadFile,user_id:int,session:AsyncSession)->LoadPingPayloadResponse:
        try:
            clean_cell_numbers=await self.csv_service.data_extraction(file=file)
            cell_numbers_length=len(clean_cell_numbers)
            user_credits_record=await credits_object.get_single_credits_record(user_id=user_id,session=session)
            credits=user_credits_record.credits_total
            if credits==0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"insufficient credits balance:{credits} for user:{user_id} to process the requested pings payload")
            #keep a record of pings
            pings_loaded_to_db=await bulk_insert_pings_input(session=session,cell_numbers=clean_cell_numbers,user_id=user_id)
            #There must be functionality for sending payload to another service
            total_numbers_received=pings_loaded_to_db['total_received']
            credits_details_response=await credits_object.update_remaining_credits_balance(number_of_records=cell_numbers_length,user_id=user_id,session=session)
            return LoadPingPayloadResponse(valid_numbers_count=total_numbers_received,invalid_number_count=10,remaining_credits=credits_details_response.remaining_credits)
        
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while uploading a pings file:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading a pings file")
        
        finally:
            await file.close()
    

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
    
    async def get_pings_overview(self,page:int,page_size:int,user_id:int,session:AsyncSession):
        base_query=select(ClientPingsOverview).where(ClientPingsOverview.created_by==user_id)
        offset=(page-1)*page_size
        count_query=select(func.count(ClientPingsOverview.pk))
        base_query=base_query.order_by(ClientPingsOverview.created_at.desc()).offset(offset).limit(page_size)
        try:
            count_query_result=await session.execute(count_query)
            count_result=count_query_result.scalar_one()
            overview_result=await session.execute(base_query)
            result=overview_result.scalars().all()
            total_pages=ceil(count_result/page_size) if count_result > 0 else 1
            return PingsOverview(total=total_pages,page=page,page_size=page_size,result=[PingOverview.model_validate(row) for row in result])
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an internal server error while getting pings overview for user:{user_id} this is the exception:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an")