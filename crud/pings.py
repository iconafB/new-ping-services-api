from fastapi import HTTPException,status,UploadFile
from sqlalchemy import select,func,update
from math import ceil
from sqlalchemy.ext.asyncio.session import AsyncSession
from models.pings import pinged_input,ClientPingsOverview,PingsInput
from models.client_tokens import pings_retrieval_tokens
from schemas.pings import PingPayload,PingsPayloadResponse,LoadPingPayloadResponse,PingStatusResponse,AllPingsPayload
from schemas.pings_overview import PingOverview,TotalPingsOverview
from schemas.clients import CurrentClientSchema
from dto.pings import PingsOverviewInsertionResult
from utils.logging.logger import define_logger
from crud.credits import CreditsCrudClass
from crud.client_tokens import ClientTokenCrud
from services.cell_number_validations.cell_number_validation import validate_sa_cell_numbers
from services.pings.pings import bulk_insert_pings_input
from services.files_services.csv_services import CSVClass
pings_logger=define_logger("pings_logger","logs/pings_route.log")
pings_overview_logger=define_logger("pings_overview_logger","logs/pings_overview.log")

credits_object=CreditsCrudClass()

class PingsCrudClass:
    #one credit per single ping
    #load pings payload
    def __init__(self):
        #this is tight coupling,needs to be resolved
        self.csv_service=CSVClass()
        self.client_tokens=ClientTokenCrud()
        self.pings_overview=PingsOverviewClass()

    #charge them even for submitting wrong data, we don't clean for free
    # create a token first


    async def load_pings_payload_crud(self,pings:PingPayload,client:CurrentClientSchema,session:AsyncSession)->PingsPayloadResponse:

        try:
            # before loading pings, check if the credits balance matches
            credits_record=await credits_object.get_single_credits_record(client_id=client.client_id,session=session)
            credits=credits_record.credits_total
            pings_length=len(pings.cell_numbers)
            if credits==0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"insufficient credits balance:{credits} for client:{client.client_id} to process the requested pings payload")
            # validate the cell numbers an clean the cell numbers
            validated_cell_numbers=validate_sa_cell_numbers(pings.cell_numbers)
            invalid_count=validated_cell_numbers["invalid_count"]
            valid_numbers=validated_cell_numbers["valid_numbers"]
            valid_count=validated_cell_numbers["valid_count"]
            # one ping per unit credit
            number_of_records=len(valid_numbers)
            updated_details=await credits_object.update_remaining_credits_balance(number_of_records=number_of_records,user_id=client.client_id,session=session)
            # generate and insert new token associated with a user
            token=await self.client_tokens.insert_client_token(user_id=client.client_id,session=session)
            # send the pings to the pings service and  to dedago service
            # input the pings into a table locally
            pings_loaded_to_db=await bulk_insert_pings_input(session=session,cell_numbers=valid_numbers,user_id=client.client_id,token_id=token.pk)
            #insert the total pings submitted for general overview
            pings_overview=await self.pings_overview.insert_total_pings_overview(session=session,client=client,total_pings=pings_loaded_to_db.total_pings_processed)
            #capture the total number of pings added
            print("print the returned token")
            print(pings_loaded_to_db)
            print("print the total overview insertion")
            print(pings_overview.total_pings)
            # commit these numbers to a database table
            pings_logger.info(f"valid count cell numbers:{valid_count}, and invalid count:{invalid_count}")
            return LoadPingPayloadResponse(valid_numbers_count=valid_count,invalid_number_count=invalid_count,remaining_credits=updated_details.remaining_credits,token=token.token)
        
        except HTTPException:
            raise

        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while load pings:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="an internal server error occurred while loading pings")

    async def load_pings_using_a_file_upload_crud(self,file:UploadFile,client:CurrentClientSchema,session:AsyncSession)->LoadPingPayloadResponse:
        try:
            clean_cell_numbers=await self.csv_service.data_extraction(file=file)
            cell_numbers_length=len(clean_cell_numbers)
            user_credits_record=await credits_object.get_single_credits_record(client_id=client.client_id,session=session)
            credits=user_credits_record.credits_total
            #search if credits are enough 
            if credits==0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"insufficient credits balance:{credits} for user:{client.client_id} to process the requested pings payload")
            #create token and insert it on the pings table
            token=await self.client_tokens.insert_client_token(user_id=client.client_id,session=session)
            #keep a record of pings
            pings_loaded_to_db=await bulk_insert_pings_input(session=session,cell_numbers=clean_cell_numbers,user_id=client.client_id,token_id=token.pk)
            #There must be functionality for sending payload to another service
            total_numbers_received=pings_loaded_to_db.total_pings_received
            total_pings_processed=pings_loaded_to_db.total_pings_processed
            #duplicate_pings=pings_loaded_to_db.duplicate_pings
            pings_total_overview=await self.pings_overview.insert_total_pings_overview(session=session,client=client,total_pings=total_pings_processed)
            credits_details_response=await credits_object.update_remaining_credits_balance(number_of_records=cell_numbers_length,user_id=client.client_id,session=session)
            #the user should get the token to fetch the pings
            return LoadPingPayloadResponse(valid_numbers_count=total_numbers_received,invalid_number_count=10,remaining_credits=credits_details_response.remaining_credits,token=token.token)
        except HTTPException:
            raise

        except Exception:
            pings_logger.exception(f"an internal server error occurred while uploading a pings file")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading a pings file")
        
        finally:
            await file.close()
    
    #this method can be made 
    async def check_pings_status(self,token:str,user_id:int,session:AsyncSession):
        #validate the existance of the token
        token_query=select(pings_retrieval_tokens.token_hash,pings_retrieval_tokens.pk).where(pings_retrieval_tokens.token_hash==token).where(pings_retrieval_tokens.client_id==user_id)
        try:
           token_query_result=await session.execute(token_query)
           token_result=token_query_result.one_or_none()
           if token_result is None:
               raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid token provided")
           
           pings_query=select(PingsInput.pinged_status,PingsInput.is_pinged).where(PingsInput.token_id==token_result.pk)
           pings_result=await session.execute(pings_query)
           result=pings_result.first()
           # Grammar chief, Grammar!!!!!
           if result.pinged_status=="Pending":
               return PingStatusResponse(token=token,message=f"pings are not ready to be downloaded")
           # Think about returning everything if the pings are ready
           return PingStatusResponse(token=token,message=f"Pings are ready to be downloaded")
        
        except HTTPException:
            raise

        except Exception:
            pings_logger.exception(f"an internal server error occurred while checking the pings status")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while checking token:{token} with user id:{user_id}")
        

    async def get_all_pings_ready_for_download(self,token:str,session:AsyncSession,user_id:int):
        #search for the token
        token_query=select(pings_retrieval_tokens.token_hash,pings_retrieval_tokens.pk).where(pings_retrieval_tokens.token_hash==token).where(pings_retrieval_tokens.client_id==user_id).where(pings_retrieval_tokens.is_active==False)
        try:
            token_query_result=await session.execute(token_query)
            token=token_query_result.one_or_none()
            #verify token existence and legitimacey, spelling chief!!!!
            if token is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Invalid token provided")
            pings_status_query=select(PingsInput.pinged_status,PingsInput.is_pinged).where(PingsInput.token_id==token.pk)
            pings_result=await session.execute(pings_status_query)
            result=pings_result.first()
            #pings are not ready
            if result.pinged_status=='Pending':
                return
             # on the tokens table update,the is_used column,used_at column,is_active
            token_stmt=(update(pings_retrieval_tokens).where(pings_retrieval_tokens.pk==token.pk).values(used_at=func.now(),is_active=False))
            await session.execute(token_stmt)
            await session.commit()
            #fetch the pinged cell number, update the pinged_status and invalidate the token submitted
            pings_query=select(PingsInput.cell_number).where(PingsInput.token_id==token.pk)
            pings_result=await session.execute(pings_query)
            results=pings_result.scalars().all()
            message=f"pings retrieved successfully"
            return AllPingsPayload(message=message,cell_numbers=[])
        
        except HTTPException:
            raise

        except Exception as e:
            pings_logger.exception(f"an internal server error occurred while fetching pings {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching pings")

    async def fetch_pings_crud(self,pings_id:str,user_id:int,session:AsyncSession):
        try:
            return False
        except HTTPException: 
            raise
        except Exception:
            pings_logger.exception(f"an internal server error occurred while fetching pings for user:{user_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching pinggs for user:{user_id}")
    
    async def test_pings(self,session:AsyncSession):
        stmt=select(pinged_input).limit(5)
        try:
            result_query=await session.execute(stmt)
            return result_query.all()
        
        except Exception:
            pings_logger.exception(f"an internal server error occurred")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred")
    
    async def get_pings_overview(self,page:int,page_size:int,client:CurrentClientSchema,session:AsyncSession):
        base_query=select(ClientPingsOverview).where(ClientPingsOverview.created_by==client.client_id)
        offset=(page-1)*page_size
        count_query=select(func.count(ClientPingsOverview.pk))
        base_query=base_query.order_by(ClientPingsOverview.created_at.desc()).offset(offset).limit(page_size)
        try:
            count_query_result=await session.execute(count_query)
            count_result=count_query_result.scalar_one()
            overview_result=await session.execute(base_query)
            result=overview_result.scalars().all()
            return TotalPingsOverview(total=count_result,page=page,page_size=page_size,results=[PingOverview.model_validate(row) for row in result])
        except HTTPException:
            raise
        except Exception:
            pings_logger.exception(f"an internal server error while getting pings overview for client:{client.client_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while  fetching pings overview")
        

class PingsOverviewClass:

    def __init__(self):
        pass

    async def insert_total_pings_overview(self,session:AsyncSession,client:CurrentClientSchema,total_pings:int):
        total_overview_insert=ClientPingsOverview(client_name=client.client_name,total_pings_sent=total_pings,created_by=client.client_id)
        session.add(total_overview_insert)
        try:
            await session.commit()
            await session.refresh(total_overview_insert)
            pings_overview_logger.info(f"a total of {total_overview_insert.total_pings_sent} inserted by client:{total_overview_insert.client_name}")
            return PingsOverviewInsertionResult(pk=total_overview_insert.pk,total_pings=total_overview_insert.total_pings_sent,created_by=total_overview_insert.created_by)
        except HTTPException:
            raise

        except Exception:
            await session.rollback()
            pings_overview_logger.exception(f"an internal server error occurred while inserting total pings for user:{client.client_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while capturing the total number of records")



    async def get_all_pings_overview(self,session:AsyncSession,page:int,page_size:int,user_id:int):
        offset=(page-1)*page_size
        total_count_query=select(func.count(ClientPingsOverview.pk)).where(ClientPingsOverview.created_by==user_id)
        pings_query=select(ClientPingsOverview).where(ClientPingsOverview.created_by).order_by(ClientPingsOverview.created_by.desc()).offset(offset).limit(page_size)
        try:
            total_pings=await session.execute(total_count_query)
            total_pings_result=total_pings.scalar_one()
            total=await session.execute(pings_query)
            results=total.scalars().all()
            return TotalPingsOverview(total=total_pings_result,page=page,page_size=page_size,results=[PingOverview(row) for row in results])
        
        except HTTPException:
            raise
        except Exception:
            pings_overview_logger.exception(f"an internal server error occurred while fetching pings overview")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching all ping overview")
    


