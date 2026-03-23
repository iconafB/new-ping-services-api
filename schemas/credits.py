from pydantic import BaseModel,ConfigDict
from datetime import datetime
from typing import List
class CreateCredits(BaseModel):
    credits_amount:int

class CreateCreditsResponse(BaseModel):
    credits_id:int
    credits_total:int
    created_by:int
    



class UserCreditsHistoryItem(BaseModel):
    history_id:int
    credits_amount:int
    created_by:int
    transaction_type:str
    is_active:bool
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)

class UserCreditsHistoryResponse(BaseModel):
    page:int
    page_size:int
    total_records:int
    total_pages:int
    credits_history:List[UserCreditsHistoryItem]


class DeleteCreditsHistory(BaseModel):
    message:str

class UpdateCreditsRemainingCredits(BaseModel):
    remaining_credits:int
    records_to_be_processed:int
