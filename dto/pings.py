from dataclasses import dataclass


@dataclass(slots=True,frozen=True)
class PingsBulkInsertResult:
    total_pings_received:int
    total_pings_processed:int
    duplicate_pings:int


""" 
class PingsOverview(BaseModel):
    pk:int
    total_pings:int
    created_by:int 
    
"""

@dataclass(slots=True,frozen=True)
class PingsOverviewInsertionResult:
    pk:int
    total_pings:int
    created_by:int
