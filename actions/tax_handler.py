from agents.player_agent.player_agents import PlayerAgent
from .base_handler import ActionHandler
from game.game_state import GameState

class TaxHandler(ActionHandler):
    def execute(self, game_state: GameState, player_id: int, player_agent: PlayerAgent):
        game_state.players[player_id]["coins"] += 3
        player_agent.coins += 3
        
        return game_state