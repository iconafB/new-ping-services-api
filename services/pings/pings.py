from fastapi import HTTPException,status,BackgroundTasks
from sqlalchemy.ext.asyncio.session import AsyncSession
import httpx
from dto.pings import PingsBulkInsertResult
from sqlalchemy.dialects.postgresql import insert as pg_insert
from models.pings import PingsInput
from utils.logging.logger import define_logger
pings_logger=define_logger("pings_logger","logs/pings_route.log")


#Put everything into a class

def chunked(values: list[str], size: int):
    for i in range(0, len(values), size):
        yield values[i:i + size]

#for this bulk insert, we need to load a token

async def bulk_insert_pings_input(session: AsyncSession,cell_numbers: list[str],user_id: int,token_id:int,pinged_status: str = "Pending",chunk_size: int = 1000) -> dict:
    
    inserted_count = 0
    try:
        for batch in chunked(cell_numbers, chunk_size):
            rows=[
                {
                    "cell_number": cell_number,
                    "pinged_status": pinged_status,
                    "created_by": user_id,
                    "token_id":token_id
                }
                for cell_number in batch
                ]

            stmt=(pg_insert(PingsInput).values(rows).on_conflict_do_nothing(index_elements=[PingsInput.cell_number]).returning(PingsInput.ping_pk))
            result = await session.execute(stmt)
            inserted_count += len(result.scalars().all())
        await session.commit()
        cell_numbers_length=len(cell_numbers)

        pings_logger.info(f"user:{user_id} loaded pings records equal to:{cell_numbers_length}")

        return  PingsBulkInsertResult(total_pings_received=cell_numbers_length,total_pings_processed=inserted_count,duplicate_pings=len(cell_numbers) - inserted_count) 
    
    except Exception as e:
        await session.rollback()
        pings_logger.exception(f"an exception occurred while loading records into the database:{str(e)}")
        raise


class PingsClass:
    
    async def send_pings_to_dedago(self):
        try:
            return
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an exception occurred while sending pings to dedago:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An exception occurred while sending pings to dedago")
        
    async def fetch_pings_from_other_services(self):
        try:
            return
        except HTTPException:
            raise
        except Exception as e:
            pings_logger.exception(f"an exception occurred while fetching pings:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An exception occurred while fetching pings")
        

