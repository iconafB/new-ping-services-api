from pydantic import BaseModel,EmailStr

class CreateClient(BaseModel):
    client_name:str
    email:EmailStr
    password:str
    

class CreateClientResponse(BaseModel):
    client_id:int
    first_name:str
    last_name:str
    email:str

class GetAllUsersResponse(BaseModel):
    pass

class LoginUser(BaseModel):
    email:str
    password:str

class LoginUserResponse(BaseModel):
    pass

