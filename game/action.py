from pydantic import BaseModel
from typing import Optional

class Action(BaseModel):
    type: str
    target: Optional[int] = None
    rationale: Optional[str] = None