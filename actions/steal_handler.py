from agents.player_agent.player_agents import PlayerAgent
from .base_handler import ActionHandler
from game.game_state import GameState

# class StealHandler(ActionHandler):
#     def execute(self, game_state: GameState, player_id: int, target_id: int, target_agent: PlayerAgent, player_agent: PlayerAgent):
#         steal_amount = min(2, game_state.players[target_id]["coins"])
        
#         game_state.players[target_id]["coins"] -= steal_amount
#         game_state.players[player_id]["coins"] += steal_amount
        
#         target_agent.coins -= steal_amount
#         player_agent.coins += steal_amount
        
#         return game_state

import logging

class StealHandler(ActionHandler):
    def execute(self, game_state: GameState, player_id: int, target_id: int, target_agent: PlayerAgent, player_agent: PlayerAgent):
        steal_amount = min(2, game_state.players[target_id]["coins"])

        # Update game state
        game_state.players[target_id]["coins"] -= steal_amount
        game_state.players[player_id]["coins"] += steal_amount

        # Update player agents
        target_agent.coins -= steal_amount
        player_agent.coins += steal_amount

        logging.info(f"Final game state after steal action: {game_state}")
        return game_state