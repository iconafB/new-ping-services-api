from sqlalchemy.ext.asyncio.session import AsyncSession
from fastapi import status,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from models.admin import Admin
from utils.logging.logger import define_logger
from schemas.admin import CreateAdmin,CreateAdminResponse
from utils.auth.security import hash_password,verify_password

admin_logger=define_logger("admin_logger","logs/admin_route.log")

"""
    implement a class that performs crud for the admin entity on the system
    this class will need sessions for this

"""

class AdminstrationCrudClass:
    # create admin user
    # get all admin users
    # update admin user details
    # remove admin user details
    # get single admin details
    
    pass

class AdminAuthCrudClass:
    
    async def register_new_admin(create_admin:CreateAdmin,session:AsyncSession):
        admin_query=select(Admin).where(Admin.email==create_admin.email)
        hashed_password=hash_password(create_admin.password)
        try:
            result=(await session.execute(admin_query)).scalar_one_or_none()
            if result is not None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"admin already exists")
            new_admin=Admin(email=create_admin.email,password=hashed_password,first_name=create_admin.first_name,last_name=create_admin.last_name)
            session.add(new_admin)
            await session.commit()
            await session.refresh(new_admin)
            admin_logger.info(f"new admin:{new_admin.email} registered")
            return new_admin
        except Exception as e:
            admin_logger.exception(f"an internal server error occurred while creating new admin:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"an internal server error occurred while creating new admin:{str(e)}")
        
    async def login_admin_crud(form_data:OAuth2PasswordRequestForm,session:AsyncSession):
        user_email=form_data.username
        user_password=form_data.password
        user_query=select(Admin).where(Admin.email==user_email)
        try:
            result=(await session.execute(user_query)).scalar_one_or_none()
            if result is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization",headers={"WWW-Authenticate": "Bearer"})
            if not verify_password(user_password,result.password):
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail=f"Invalid authorization")
            admin_logger.info(f"user:{result.id} with email:{result.email} logged in")
            return result
        
        except Exception as e:
            admin_logger.exception(f"an internal server error while login user:{str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"An internal server error occurred while login user")
    