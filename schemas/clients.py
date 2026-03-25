from pydantic import BaseModel,EmailStr,ConfigDict
from datetime import datetime
from typing import List
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

class ClientsSchema(BaseModel):
    client_id:int
    client_email:str
    client_name:str
    created_at:datetime
    is_active:bool

class AllClientsSchema(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    client_name:str
    client_id:int
    email:str
    created_at:datetime
    is_active:bool

class GetAllClientsSchema(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[AllClientsSchema]

class UpdateClientSchema(BaseModel):
    client_name:str | None
    client_email:EmailStr | None

class DeleteClientSchema(BaseModel):
    message:str