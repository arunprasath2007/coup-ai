from abc import ABC, abstractmethod
from game.game_state import GameState

class ActionHandler(ABC):
    @abstractmethod
    def execute(self, game_state: GameState, player_id: int):
        pass