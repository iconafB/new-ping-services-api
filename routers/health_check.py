from fastapi import APIRouter,status
from datetime import datetime,timezone,timedelta

health_check_router=APIRouter(prefix="/v1/health",tags=["HEALTH CHECK"])
sa_time_zone=timezone(timedelta(hours=2))
@health_check_router.get("",status_code=status.HTTP_200_OK,description="Check the health status of the service")
async def health_check():
    sa_datetime=datetime.now(sa_time_zone)    

    return {"message":"client api is healthy","status":"ok","date":sa_datetime.isoformat()}

