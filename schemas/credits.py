from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List
class CreateCredits(BaseModel):
    credits_total:int

class CreateCreditsResponse(BaseModel):
    credits_id:int
    credits_total:int
    created_by:int


class UserCreditsHistoryItem(BaseModel):
    history_id:int
    credits_amount:int
    created_by:int
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class UserCreditsHistoryResponse(BaseModel):
    items:List[UserCreditsHistoryItem]
    page:int
    page_size:int
    total_records:int
    total_pages:int


