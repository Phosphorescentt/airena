from typing import Optional, List
from dataclasses import dataclass


@dataclass
class ReviewInformation:
    conversation_id: int
    total_participants: int
    first_message: int
    last_message: Optional[int]
    system_prompt: str
    history: List[str]
