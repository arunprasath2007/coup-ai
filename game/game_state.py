from pydantic import BaseModel
from typing import Dict, Any, List

class GameState(BaseModel):
    players: Dict[int, Dict[str, Any]]
    current_player: int
    deck: List[str]