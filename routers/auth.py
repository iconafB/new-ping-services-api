from fastapi import APIRouter,status,HTTPException
auth_router=APIRouter(tags=["Authentication Routes"],prefix="/auth")

@auth_router.post("/register")
async def register_user():
    """
        Register a new user by providing the following fields:
        1. email
        2. password
        3. first name
        4. last name
    """
    return True

@auth_router.post("/login")
async def login_users():
    """
        login registered users by providing the following fields
        1. email
        2. password
    """
    return True

@auth_router.post("/admin/register")
async def register_new_admin():
    """
    register admin by providing the following fields
    1. email/username
    2. password
    3. first name
    4. last name
    5. is_admin
    """
    return True



@auth_router.post("/admin/login")
async def login_admin():
    """
        login the admin using the following fields
        1. password 
        2. email
    """
    return True
