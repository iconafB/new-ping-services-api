from fastapi import status,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select,func,update
from math import ceil
from utils.logging.logger import define_logger
from models.credits import Credits,Credits_History_Table,TransactionType
from schemas.clients import CurrentClientSchema
from schemas.credits import CreateCreditsResponse,UserCreditsHistoryResponse,UserCreditsHistoryItem,DeleteCreditsHistory,UpdateCreditsRemainingCredits



credits_logger=define_logger("credits_logger","logs/credits_route.log")

class CreditsCrudClass:
    # load/create credits on the service
    async def load_client_credits(self,credits_amount:int,user_id:int,session:AsyncSession)->CreateCreditsResponse:
        #find the user/client to load credits for,raise an exception if the users/client does not exist
        user_query_stmt=select(Credits).where(Credits.created_by==user_id)
        try:
            #check if the user exist
            user_credits_result=(await session.execute(user_query_stmt)).scalar_one_or_none()
            if user_credits_result is None:
                #This person does not have a credits history therefore create new record
                new_user_credits=Credits(credits_balance=credits_amount,created_by=user_id)
                session.add(new_user_credits)
                await session.flush()
                new_user_credits_history=Credits_History_Table(credits_amount=credits_amount,created_by=user_id,transaction_type=TransactionType.Deposit,is_active=True)
                session.add(new_user_credits_history)
                await session.commit()
                await session.refresh(new_user_credits)
                credits_logger.info(f"user:{user_id} loaded credits:{credits_amount} total:{new_user_credits.credits_balance}")
                return CreateCreditsResponse(credits_id=new_user_credits.credits_id,credits_total=new_user_credits.credits_balance,created_by=new_user_credits.created_by)
            
            #the user exist,they have credits history
            else:
                user_credits_result.credits_balance+=credits_amount
                created_by=user_credits_result.created_by
                new_history_record=Credits_History_Table(credits_amount=credits_amount,created_by=created_by,transaction_type=TransactionType.Deposit,is_active=True)
                session.add(new_history_record)
                await session.commit()
                await session.refresh(user_credits_result)
                credits_logger.info(f"user:{user_id} loaded credits:{credits_amount} total:{user_credits_result.credits_balance}")
                return CreateCreditsResponse(credits_id=user_credits_result.credits_id,credits_total=user_credits_result.credits_balance,created_by=user_credits_result.created_by)

        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            credits_logger.exception(f"an internal server error occurred while loading credits for user:{user_id},error:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading credits for user:{user_id}")
    
    # get all credits, credits history, this history should be paginated
    async def get_all_credits_history_for_a_user(self,page:int,page_size:int,user_id:int,session:AsyncSession)->UserCreditsHistoryResponse:
        offset=(page - 1)*page_size
        base_query=select(Credits_History_Table)
        count_query=select(func.count(Credits_History_Table.history_id)).where(Credits_History_Table.created_by==user_id)
        base_query=(base_query.order_by(Credits_History_Table.created_at.desc()).where(Credits_History_Table.created_by==user_id).offset(offset).limit(page_size))

        try:
            total_records_result=await session.execute(count_query)
            total_records=total_records_result.scalar_one()
            history_result=await session.execute(base_query)
            history_records=history_result.scalars().all()
            total_pages=ceil(total_records / page_size) if total_records > 0 else 1
            return UserCreditsHistoryResponse(page=page,page_size=page_size,total_records=total_records,total_pages=total_pages,credits_history=[UserCreditsHistoryItem.model_validate(record) for record in history_records])
        except HTTPException:
            raise
        

        except Exception:
            credits_logger.exception(f"an internal server error occurred while using getting credit history")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching credits history for user:{user_id}")
    
    # get single credits record
    async def get_single_credits_record(self,client:CurrentClientSchema,session:AsyncSession)->CreateCreditsResponse:

        credits_stmt=select(Credits).where(Credits.created_by==client.client_id)
        try:
            credits=await session.execute(credits_stmt)
            results=credits.scalar_one_or_none()
            if results.is_active==False:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"No active credit balance for user:{client.client_id}")
            if results is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user:{client.client_id} has no credits history")
            return CreateCreditsResponse(credits_id=results.credits_id,credits_total=results.credits_balance,created_by=results.created_by)
        
        except HTTPException:
            raise

        except Exception as e:
            credits_logger.exception(f"an internal server error occurred while get credits records:{client.client_id},{str(e)}")

            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching credits record for user:{client.client_id}")
    
    # remove credits history,soft delete
    async def delete_credits_history_db(self,client_id:int,session:AsyncSession):
        credits_history_stmt=select(Credits_History_Table).where(Credits_History_Table.created_by==client_id)
        credits_stmt=select(Credits).where(Credits.created_by==client_id).where(Credits.is_active==True)
        try:
            result=await session.execute(credits_history_stmt)
            credit_history=result.scalars().fetchall()
            if not credit_history:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"record does not exist")
            update_stmt=(update(Credits_History_Table).where(Credits_History_Table.created_by==client_id).values(is_active=False))
            await session.execute(update_stmt)
            current_credits_balance=await session.execute(credits_stmt)
            credit_balance_result=current_credits_balance.scalar_one_or_none()
            #this is debatable
            if credit_balance_result is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"The current user:{client_id} has not active balance")
            credit_balance_result.is_active=False
            await session.commit()
            credits_logger.info(f"Credits history for user {client_id} deleted successfully")
            return DeleteCreditsHistory(message=f"Credits history for user {client_id} deleted successfully")
        except HTTPException:
            raise

        except Exception as e:
            await session.rollback()
            credits_logger.exception(f"an internal server error occurred while deleting credits history:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while deleting credits history:{client_id}")
    
    async def log_credits_history(self,credit_amount:int,created_by:int,session:AsyncSession):
        try:
            new_history_record=Credits_History_Table(credit_amount=credit_amount,created_by=created_by,is_active=True)
            session.add(new_history_record)
            await session.commit()
        except Exception as e:
            credits_logger.exception(f"an exception occurred while reading credits history:{str(e)}")
            #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while reading credits history")

    #this method should get the total number of records submitted,since one record is equal to one credit and update credits accordingly
    async def update_remaining_credits_balance(self,number_of_records:int,user_id:int,session:AsyncSession)->UpdateCreditsRemainingCredits:
        #find the record
        record_query=select(Credits).where(Credits.created_by==user_id)
        #check if the number of record is valid,only positive values
        if number_of_records<0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Invalid update value:{number_of_records},value must be greated than zero")
        
        try:
            credits_record=await session.execute(record_query)
            credits_result=credits_record.scalar_one_or_none()
            if credits_result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"No credits record balance exist for user:{user_id}")
            current_credits=credits_result.credits_balance or 0
            # Subtraction higher than available balance

            if number_of_records > current_credits:
                new_balance=0
                credits_result.credits_balance=new_balance
                number_of_records_processed=number_of_records
                #update the history
                add_credits=Credits_History_Table(credits_amount=number_of_records,transaction_type=TransactionType.Withdrawal,created_by=user_id,is_active=True)
                session.add(add_credits)
                await session.commit()
                await session.refresh(credits_result)
                return UpdateCreditsRemainingCredits(remaining_credits=credits_result.credits_balance,records_to_be_processed=number_of_records_processed)
            
            new_balance=current_credits - number_of_records
            credits_result.credits_balance=new_balance
            #update the history table
            add_credits=Credits_History_Table(credits_amount=number_of_records,transaction_type=TransactionType.Withdrawal,created_by=user_id,is_active=True)
            session.add(add_credits)
            await session.commit()
            await session.refresh(credits_result)
            
            return UpdateCreditsRemainingCredits(remaining_credits=credits_result.credits_balance,records_to_be_processed=number_of_records)
        except HTTPException:
            raise
        except Exception as e:
            credits_logger.exception(f"an exception occurred while updating the remaining credits balance by user:{user_id}, exception:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while updating the credits balance for user:{user_id}")
     
    async def update_withdrawals_credits_history(self,user_id:int,withdrawn_amount:int,session:AsyncSession):
        try:
            return
        except HTTPException:
            raise
        except Exception as e:
            credits_logger.exception(f"an exception occurred while updating withdrawal amount:{withdrawn_amount} for user:{user_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while updating withdrawals for user:{user_id} for amount:{withdrawn_amount}")
    
    async def update_deposits_credits_history(self,user_id:int,deposited_amount:int,session:AsyncSession):
        try:
            return
        except HTTPException:
            raise
        except Exception as e:
            credits_logger.exception(f"an internal server error occurred while depositing into")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server")

    async def get_all_deposits(self,client:CurrentClientSchema,session:AsyncSession,page:int,page_size:int):
        offset=(page-1)*page_size
        deposit_query=select(Credits_History_Table).where(Credits_History_Table.created_by==client.client_id).where(Credits_History_Table.transaction_type==TransactionType.Deposit).order_by(Credits_History_Table.created_at.desc()).offset(offset).limit(page_size)
        count_query=select(func.count(Credits_History_Table.history_id)).where(Credits_History_Table.created_by==client.client_id)
        try:
            count_query_result=await session.execute(count_query)
            total=count_query_result.scalar_one()
            deposit_results=await session.execute(deposit_query)
            results=deposit_results.scalars().all()
            total_pages=ceil(total / page_size) if total > 0 else 1
            return UserCreditsHistoryResponse(page=page,page_size=page_size,total_records=total,total_pages=total_pages,credits_history=[UserCreditsHistoryItem.model_validate(record) for record in results])
        except HTTPException:
            raise
        except Exception:
            credits_logger.exception(f"an internal server error occurred while fetching all the deposits for user:{client.client_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occured while fetching all the deposits for user:{client.client_id}") 

    async def get_all_withdrawals(self,client:CurrentClientSchema,session:AsyncSession,page:int,page_size:int):

        offset=(page-1)*page_size
        deposit_query=select(Credits_History_Table).where(Credits_History_Table.created_by==client.client_id).where(Credits_History_Table.transaction_type==TransactionType.Withdrawal).order_by(Credits_History_Table.created_at.desc()).offset(offset).limit(page_size)
        count_query=select(func.count(Credits_History_Table.history_id)).where(Credits_History_Table.created_by==client.client_id)
        try:
            count_query_result=await session.execute(count_query)
            total=count_query_result.scalar_one()
            deposit_results=await session.execute(deposit_query)
            results=deposit_results.scalars().all()
            #this is nonsense
            total_pages=ceil(total / page_size) if total > 0 else 1

            return UserCreditsHistoryResponse(page=page,page_size=page_size,total_records=total,total_pages=total_pages,credits_history=[UserCreditsHistoryItem.model_validate(record) for record in results])
        except HTTPException:
            raise
        except Exception:
            credits_logger.exception(f"an internal server error occurred while fetching all the deposits for user:{client.client_id}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occured while fetching all the deposits for user:{client.client_id}")   

