from pydantic import BaseModel
from datetime import datetime
from typing import List
class TokenInsertionResponse(BaseModel):
    pk:int
    token:str
    created_at:datetime


class TokenSchema(BaseModel):
    token_hash:str
    client_id:int
    pings_id:int
    created_at:datetime
    is_used:bool
    used_at:datetime
    is_active:bool

class AllTokensSchema(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[TokenSchema]