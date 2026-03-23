import re
from typing import Iterable


def validate_sa_cell_numbers(cell_numbers: Iterable[str]) -> dict:
    """
    Validate a list of South African cell numbers.

    Rules used:
    - Accept local format: 0XXXXXXXXX (10 digits total)
    - Accept international format: 27XXXXXXXXX (11 digits total, no + after normalization)
    - Mobile numbers must start with:
        - local: 06, 07, 08
        - international: 276, 277, 278
    """

    valid_numbers = []
    invalid_count = 0

    for raw in cell_numbers:
        if raw is None:
            invalid_count += 1
            continue

        # Keep digits only, so formats like "+27 82 123 4567" still work
        normalized = re.sub(r"\D", "", str(raw).strip())
        is_valid = False
        local_format = None

        # Local format: 0XXXXXXXXX
        if len(normalized) == 10 and normalized.startswith(("06", "07", "08")):
            is_valid = True
            local_format = normalized

        # International format
        elif len(normalized) == 11 and normalized.startswith(("276", "277", "278")):
            is_valid = True
            local_format = "0" + normalized[2:]

        if is_valid:
            valid_numbers.append(local_format)
        else:
            invalid_count += 1

    return {
        "invalid_count": invalid_count,
        "valid_numbers": valid_numbers,
        "valid_count": len(valid_numbers),
    }