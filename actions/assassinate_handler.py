from agents.player_agent.player_agents import PlayerAgent
from display.console_display import ConsoleDisplay
from .base_handler import ActionHandler
from game.game_state import GameState

class AssassinateHandler(ActionHandler):
    def __init__(self):
        self.display = ConsoleDisplay()    
    
    def execute(self, game_state: GameState, player_id: int, target_id: int, target_agent: PlayerAgent, player_agent: PlayerAgent):
        # Deduct coins from the assassinating player
        game_state.players[player_id]["coins"] -= 3
        player_agent.coins -= 3
        
        # Check if the target player has any influence left
        if game_state.players[target_id]["influence_count"] > 0:
            # Let the target player choose which influence to lose
            discarded_role = target_agent.choose_influence_to_lose(game_state)
        
            # Update the game state
            game_state.players[target_id]["influence_count"] -= 1
            
            if game_state.players[target_id]["influence_count"] == 0:
                self.display.display_elimination(target_id)
            
            game_state.deck.append(discarded_role.name)  # Return the discarded role to the deck
        
        return game_state

