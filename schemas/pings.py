from pydantic import BaseModel
from typing import List

class PingsCellNumber(BaseModel):
    cell_number:str

class PingPayload(BaseModel):
    payload:List[PingsCellNumber]

class PingsPayloadResponse(BaseModel):
    number_of_pings_uploaded:int
    pings_id:str
    message:str