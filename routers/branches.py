from fastapi import status,APIRouter

branch_router=APIRouter(tags=["Branches"],prefix="/branches")

@branch_router.post("",status_code=status.HTTP_201_CREATED,description="Create A new branch")
async def create_new_branch():
    return

@branch_router.get("",status_code=status.HTTP_200_OK,description="Get all branches")
async def get_all_branches():
    return True

@branch_router.get("/{branch_id}",status_code=status.HTTP_200_OK,description="Fetch a single branch by branch id")
async def get_single_branch():
    return True

@branch_router.patch("/{branch_id}",status_code=status.HTTP_200_OK,description="Update branch details")
async def update_branch_details():
    return True

@branch_router.delete("/{branch_id}",status_code=status.HTTP_202_ACCEPTED,description="Delete the branch")
async def delete_branch():
    return True

