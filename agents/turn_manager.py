from typing import Tuple
from display.console_display import ConsoleDisplay
from game.game_state import GameState


class TurnManager:
    def __init__(self, num_players: int, display: ConsoleDisplay):
        self.num_players = num_players
        self.display = display

    def next_turn(self, game_state: GameState) -> Tuple[GameState, str]:
        current_player = game_state.current_player
        for _ in range(self.num_players):
            current_player = (current_player + 1) % self.num_players
            if game_state.players[current_player]["influence_count"] > 0:
                game_state.current_player = current_player
                self.display.display_game_state(game_state)
                return game_state, f"Player {current_player}'s turn"
        
        return game_state, "Game Over - No players with influence remaining"

    def is_game_over(self, game_state: GameState) -> bool:
        players_with_influence = sum(1 for player in game_state.players.values() if player["influence_count"] > 0)
        return players_with_influence <= 1