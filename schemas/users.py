from pydantic import BaseModel,EmailStr

class CreateUser(BaseModel):
    first_name:str
    last_name:str
    password:str
    email:EmailStr
    

class CreateUserResponse(BaseModel):
    id:int
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

