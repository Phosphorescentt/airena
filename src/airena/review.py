from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ReviewInformation:
    total_participants: int
    first_unreviewed_message: int
    last_unreviewed_message: Optional[int]
    history: List[str]
