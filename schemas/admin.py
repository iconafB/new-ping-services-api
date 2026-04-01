from pydantic import BaseModel

class CreateAdmin(BaseModel):
    first_name:str
    last_name:str
    email:str
    password:str

class CreateAdminResponse(BaseModel):
    first_name:str
    last_name:str
    email:str



