from fastapi import status,HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy import select
from models.client_tokens import pings_retrieval_tokens
from schemas.client_tokens import TokenInsertionResponse,TokenSchema
from utils.logging.logger import define_logger
from services.client_tokens.tokens import generate_secure_token,hash_token
client_tokens_logger=define_logger("clients_logger","logs/client_tokens.log")
#these tokens should not be accessable to users
class ClientTokenCrud:

    def __init__(self):
        pass
    #insert user token
    async def insert_client_token(self,user_id:int,session:AsyncSession)->TokenInsertionResponse:
        #generate the token to insert
        #search for the token even if it's unique just to make sure
        #token_query=select(pings_retrieval_tokens).where(pings_retrieval_tokens==token).where(pings_retrieval_tokens.client_id==user_id)
        try:
            #This is useless but for security
            #generate the token
            raw_token=generate_secure_token()
            hashed_token=hash_token(raw_token)
            client_token=pings_retrieval_tokens(token_hash=hashed_token,client_id=user_id,is_used=False,is_active=True)
            session.add(client_token)
            await session.commit()
            await session.refresh(client_token)
            client_tokens_logger.info(f"user:{user_id} created token")
            return TokenInsertionResponse(pk=client_token.pk,token=client_token.token_hash,created_at=client_token.created_at)
        
        except HTTPException:
            raise
        except Exception as e:
            await session.rollback()
            client_tokens_logger.exception(f"an internal server error occurred while inserting token for user {user_id}:{e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while inserting token for user:{user_id}")
        
    #get all tokens, this is for admin
    async def get_all_tokens(self,user_id:int,session:AsyncSession,page:int,page_size:int):

        try:
            return
        except Exception as e:
            raise

    #get all users tokens
    async def get_all_user_specific_tokens(self,user_id:int,session:AsyncSession,page:int,page_size:int):
        try:
            return
        
        except Exception as e:
            client_tokens_logger.exception(f"an exception occurred while fetching tokens for user:{user_id} tokens{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetch user tokens")
    
    #get single token
    async def get_single_client_token(self,user_id:int,token:str,session:AsyncSession):
        single_client_token_query=select(pings_retrieval_tokens).where(pings_retrieval_tokens.client_id==user_id & pings_retrieval_tokens.token_hash==token)
        try:
            single_token=await session.execute(single_client_token_query)
            result=single_token.scalar_one_or_none()
            if result is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Token does not exist")
            return TokenSchema(token_hash=result.token_hash,client_id=result.client_id,pings_id=result.pings_id,created_at=result.created_at,is_used=result.is_used,used_at=result.used_at,is_active=result.is_active)
        except Exception as e:
            client_tokens_logger.exception(f"an internal server error occurred while fetching token:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching")
        

    #deactivate token

    