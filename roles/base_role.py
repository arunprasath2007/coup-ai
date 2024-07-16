from abc import abstractmethod
from pydantic import BaseModel
from typing import List

from game.game_state import GameState
from game.action import Action

class Role(BaseModel):
    name: str
    actions: List[str]
    block_actions: List[str]

    @abstractmethod
    def get_strategies(self, game_state: GameState) -> List[str]:
        pass
    
    @abstractmethod
    def get_response_strategies(self, game_state: GameState, action: Action) -> List[str]:
        pass
    
    def __eq__(self, other):
        if isinstance(other, Role):
            return self.name == other.name
        return False

    def __hash__(self):
        return hash(self.name)

    class Config:
        eq = False

    def __str__(self):
        return self.name
