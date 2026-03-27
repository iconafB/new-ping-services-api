from pydantic import BaseModel,ConfigDict
from typing import List

class PingOverview(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    pk:int
    client_name:str
    total_pings_sent:int
    created_by:int

class TotalPingsOverview(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[PingOverview]


