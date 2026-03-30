from fastapi import HTTPException,status,Depends
from fastapi.security import HTTPBasic,HTTPBasicCredentials
import secrets
from typing import Annotated
import jwt
from sqlalchemy import select
from pwdlib import PasswordHash
from typing import Annotated
from datetime import timedelta,datetime,timezone
from sqlalchemy.ext.asyncio.session import AsyncSession
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer
from schemas.clients import CurrentClientSchema
from models.clients import Clients_Table
from config.database import get_async_session
from settings.settings import get_settings
from utils.logging.logger import define_logger

auth_logger=define_logger("auth_logger","logs/auth_route.log")
ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="/auth/login")
password_hash = PasswordHash.recommended()

security=HTTPBasic()


def hash_password(plain_password)->str:
    return password_hash.hash(plain_password)

def verify_password(plain_password,hashed_password):
    return password_hash.verify(plain_password,hashed_password)

def create_access_token(data:dict,expires_delta:timedelta | None=None)->str:
    to_encode=data.copy()
    if expires_delta:
        expire=datetime.now(timezone.utc) + expires_delta
    else:
        expire=datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt=jwt.encode(to_encode,get_settings().SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

def require_docs_auth(credentials:HTTPBasicCredentials=Depends(security)):
    settings=get_settings()
    user_ok=secrets.compare_digest(credentials.username,settings.ADMIN_USERNAME)
    pass_ok=secrets.compare_digest(credentials.password,settings.ADMIN_PASSWORD)
    if not (user_ok and pass_ok):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized",headers={"WWW-Authenticate":"Basic"})
    return True



def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        payload=jwt.decode(token,get_settings().SECRET_KEY,algorithms=[ALGORITHM])
        user_id=payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except InvalidTokenError:
        raise credentials_exception
    return user_id

#DRY Principle violeted
async def get_current_active_user(client_id:Annotated[int,Depends(get_current_user_id)],session:AsyncSession=Depends(get_async_session))->CurrentClientSchema:
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not validate credentials",headers={"WWW-Authenticate": "Bearer"})
    try:
        user_stmt=select(Clients_Table).where(Clients_Table.client_id==client_id)
        current_user=(await session.execute(user_stmt)).scalar_one_or_none()
        if current_user is None:
            raise credentials_exception
        user=CurrentClientSchema(client_id=current_user.client_id,client_email=current_user.email,client_name=current_user.client_name)
        return user

    except HTTPException:
        raise
    except Exception as e:
        auth_logger.exception(f"an internal server error occurred while fetching the current active user:{str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while fetching the current user id")
    
