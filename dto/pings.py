from dataclasses import dataclass


@dataclass(slots=True,frozen=True)
class PingsBulkInsertResult:
    total_pings_received:int
    total_pings_processed:int
    duplicate_pings:int

