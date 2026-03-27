from pydantic import BaseModel,ConfigDict
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
    token:str

class LoadPingPayloadResponse(BaseModel):
    valid_numbers_count:int
    invalid_number_count:int
    remaining_credits:int
    token:str



class PingOverview(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    pk:int
    client_name:str
    total_pings_sent:int
    created_at:datetime

class PingsOverview(BaseModel):
    total:int
    page:int
    page_size:int
    results:List[PingOverview]


#Note clients can give you same numbers to ping, don't give a damn even if those number have been submitted before process them

class PingsBulkInsert(BaseModel):
    total_pings_received:int
    total_pings_process:int
    duplicate_pings:int


class PingStatusResponse(BaseModel):
    token:str
    message:str

#Provide contactability quality on the response of, Medium, Low, and High Quality

class AllPingsPayload(BaseModel):
    message:str
    cell_numbers:list[str]