import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from pwdlib import PasswordHash
from settings.settings import get_settings
from datetime import timedelta,datetime,timezone

ALGORITHM='HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()

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

async def get_current_user():
    try:
        return True
    except Exception as e:

        raise

