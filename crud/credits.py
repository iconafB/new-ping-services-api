from fastapi import status,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select,func,update
from math import ceil
from utils.logging.logger import define_logger
from models.credits import Credits,Credits_History_Table
from schemas.credits import CreateCreditsResponse,UserCreditsHistoryResponse,UserCreditsHistoryItem,DeleteCreditsHistory
"""
Implement  a class that performs crud for the credits entity of the system
"""
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
                new_user_credits=Credits(credits_total=credits_amount,created_by=user_id)
                session.add(new_user_credits)
                await session.flush()
                new_user_credits_history=Credits_History_Table(credits_amount=credits_amount,created_by=user_id,is_active=True)
                session.add(new_user_credits_history)
                await session.commit()
                await session.refresh(new_user_credits)
                credits_logger.info(f"user:{user_id} added credits total:{new_user_credits.credits_total}")
                return CreateCreditsResponse(credits_id=new_user_credits.credits_id,credits_total=new_user_credits.credits_total,created_by=new_user_credits.created_by)
            #the user exist,they have credits history and 
            else:
                user_credits_result.credits_total+=credits_amount
                created_by=user_credits_result.created_by
                new_history_record=Credits_History_Table(credits_amount=credits_amount,created_by=created_by,is_active=True)
                session.add(new_history_record)
                await session.commit()
                await session.refresh(user_credits_result)
                credits_logger.info(f"user:{user_id} loaded credits total:{user_credits_result.credits_total}")
                return CreateCreditsResponse(credits_id=user_credits_result.credits_id,credits_total=user_credits_result.credits_total,created_by=user_credits_result.created_by)
        
        except HTTPException:
            raise

        except Exception as e:
            await session.rollback()
            credits_logger.exception(f"an internal server error occurred while loading credits for user:{user_id},error:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while loading credits for user:{user_id}")
    
    # get all credits, credits history, this history should be paginated
    async def get_all_credits_history_for_a_user(self,page:int,page_size:int,user_id:int,session:AsyncSession)->UserCreditsHistoryResponse:
        print(f"print the currently logged in user:{user_id}")
        try:
            offset=(page - 1)*page_size
            base_query=select(Credits_History_Table)
            count_query=select(func.count(Credits_History_Table.history_id)).where(Credits_History_Table.created_by==user_id)
            base_query=(base_query.order_by(Credits_History_Table.created_at.desc()).where(Credits_History_Table.created_by==user_id).offset(offset).limit(page_size))
            total_records_result=await session.execute(count_query)
            total_records=total_records_result.scalar_one()
            history_result=await session.execute(base_query)
            history_records=history_result.scalars().all()
            total_pages=ceil(total_records / page_size) if total_records > 0 else 1

            return UserCreditsHistoryResponse(
            items=[UserCreditsHistoryItem.model_validate(record)for record in history_records],
            page=page,
            page_size=page_size,
            total_records=total_records,
            total_pages=total_pages
            )
        
        except HTTPException:
            raise

        except Exception as e:
            credits_logger.exception(f"an internal server error occurred while using getting credit history:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching credits history for user:{user_id}")
    
    # get single credits record
    async def get_single_credits_record(self,user_id:int,session:AsyncSession)->CreateCreditsResponse:
        credits_stmt=select(Credits).where(Credits.created_by==user_id)
        try:
            credits=await session.execute(credits_stmt)
            results=credits.scalar_one_or_none()
            if results.is_active==False:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"No active credit balance for user:{user_id}")
            if results is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"user:{user_id} has no credits history")
            return CreateCreditsResponse(credits_id=results.credits_id,credits_total=results.credits_total,created_by=results.created_by)
        except HTTPException:
            raise

        except Exception as e:
            credits_logger.exception(f"an internal server error occurred while get credits records:{user_id},{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while fetching credits record for user:{user_id}")
    
    # remove credits history,soft delete

    async def delete_credits_history_db(self,user_id:int,session:AsyncSession):
        credits_history_stmt=select(Credits_History_Table).where(Credits_History_Table.created_by==user_id)
        credits_stmt=select(Credits).where(Credits.created_by==user_id).where(Credits.is_active==True)
        try:
            result=await session.execute(credits_history_stmt)
            credit_history=result.scalars().fetchall()
            if not credit_history:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"record does not exist")
            update_stmt=(update(Credits_History_Table).where(Credits_History_Table.created_by==user_id).values(is_active=False))
            await session.execute(update_stmt)
            current_credits_balance=await session.execute(credits_stmt)
            credit_balance_result=current_credits_balance.scalar_one_or_none()
            #this is debatable
            if credit_balance_result is None:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"The current user:{user_id} has not active balance")
            credit_balance_result.is_active=False
            await session.commit()
            credits_logger.info(f"Credits history for user {user_id} deleted successfully")
            return DeleteCreditsHistory(message=f"Credits history for user {user_id} deleted successfully")
        except HTTPException:
            raise

        except Exception as e:
            await session.rollback()
            credits_logger.exception(f"an internal server error occurred while deleting credits history:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while deleting credits history:{user_id}")
    
    async def log_credits_history(self,credit_amount:int,created_by:int,session:AsyncSession):
        try:
            new_history_record=Credits_History_Table(credit_amount=credit_amount,created_by=created_by,is_active=True)
            session.add(new_history_record)
            await session.commit()
        except Exception as e:
            credits_logger.exception(f"an exception occurred while reading credits history:{str(e)}")
            #raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while reading credits history")

