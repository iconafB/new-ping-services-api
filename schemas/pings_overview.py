from pydantic import BaseModel
from typing import List

class PingsOverview(BaseModel):
    pk:int
    total_pings:int
    created_by:int

class TotalPingsOverview(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[PingsOverview]


