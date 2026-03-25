from pydantic import BaseModel
from typing import List
from datetime import datetime
class PingsCellNumber(BaseModel):
    cell_number:str

class PingPayload(BaseModel):
    cell_numbers:list[str]

class PingsPayloadResponse(BaseModel):
    number_of_pings_uploaded:int
    pings_id:str
    message:str

class LoadPingPayloadResponse(BaseModel):
    valid_numbers_count:int
    invalid_number_count:int
    pinged_cell_numbers:list[str]
    remaining_credits:int

class PingOverview(BaseModel):
    pk:int
    client_name:str
    total_pings_sent:int
    created_at:datetime

class PingsOverview(BaseModel):
    total:int
    page:int
    page_size:int
    result:List[PingOverview]