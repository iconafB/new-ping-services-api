from pydantic import BaseModel,EmailStr
from datetime import datetime
class CreateClient(BaseModel):
    client_name:str
    email:EmailStr
    password:str
    

class CreateClientResponse(BaseModel):
    client_id:int
    client_name:str
    created_at:datetime

class GetAllUsersResponse(BaseModel):
    pass

class LoginUser(BaseModel):
    email:str
    password:str

class LoginUserResponse(BaseModel):
    pass

