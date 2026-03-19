from fastapi import APIRouter

users_router=APIRouter(tags=["Users Routes"],prefix="/users")

@users_router.post("/all")

async def register_user():
    """
        Register a new user by providing the following fields:
        1. email
        2. password
        3. first name
        4. last name
    """
    return True


@users_router.post("/login")
async def login_users():
    """
        login registered users by providing the following fields
        1. email
        2. password
    """
    return True