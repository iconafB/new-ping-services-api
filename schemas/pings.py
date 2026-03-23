from pydantic import BaseModel
from typing import List

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