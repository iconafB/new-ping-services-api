from pydantic import BaseModel,ConfigDict
from typing import List
from datetime import datetime

class PingOverview(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    pk:int
    client_name:str
    total_pings_sent:int
    created_by:int
    created_at:datetime

class TotalPingsOverview(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[PingOverview]

