import json
import random
from typing import Dict, List, Any, Tuple
from agents.action_resolver import ActionResolver
from agents.game_setup import GameSetup
from agents.player_agent.player_agents import PlayerAgent
from agents.turn_manager import TurnManager
from game.state_manager import GameStateManager
from game.game_state import GameState
from game.action import Action
from roles.base_role import Role
from roles.duke import Duke
from roles.captain import Captain
from roles.ambassador import Ambassador
from roles.assassin import Assassin
from roles.contessa import Contessa
from display.console_display import ConsoleDisplay
from utils.llm_utils import LLMUtils
from utils.role_utils import RoleUtils

import autogen

class GameMasterAgent(autogen.ConversableAgent):
    def __init__(self, num_players: int, llm_config: Dict[str, Any], **kwargs):
        super().__init__(name="GameMaster", llm_config=llm_config, **kwargs)
        self.num_players = num_players
        self.llm_config = llm_config
        self.display = ConsoleDisplay()
        self.game_setup = GameSetup(num_players, llm_config)
        self.game_state_manager = None
        self.action_resolver = None
        self.turn_manager = TurnManager(num_players, self.display)
        self.game_state = None
        self.players = []

    def setup_game(self):
        self.game_setup.setup_players()
        self.players = self.game_setup.players
        self.game_state = self.game_setup.create_initial_game_state()
        
        player_agents = {player.player_id: player for player in self.players}
        self.game_state_manager = GameStateManager(player_agents)
        self.action_resolver = ActionResolver(self.game_state_manager, self.display, self.initiate_chat, self.llm_config)

    def run_game(self):
        self.setup_game()
        self.display.display_game_state(self.game_state)
        
        while not self.turn_manager.is_game_over(self.game_state):
            current_player = self.players[self.game_state.current_player]
            
            self.display.display_conversation("GameMaster", f"Asking Player {current_player.player_id} to pick an action...")
            try:
                response = self.initiate_chat(
                    recipient=current_player,
                    message=f"PLAYER_ACTION {self.game_state.model_dump_json()}", 
                    silent=True,
                    config=self.llm_config,
                    max_turns=1
                )
                # Process the player's response
                self.process_player_response(response.summary, current_player)
            except Exception as e:
                print(e.with_traceback())
                break

        self.announce_winner()

    def process_player_response(self, response: str, player: PlayerAgent):
        if response.startswith("ACTION"):
            action = Action.parse_raw(response.split("ACTION")[-1].strip())
            self.display.display_player_turn(player.player_id, action) 
            self.game_state = self.action_resolver.resolve_action(action, self.game_state, self.players)
            self.game_state, _ = self.turn_manager.next_turn(self.game_state)
        else:
            self.display.display_conversation("GameMaster", "Invalid response. Skipping turn.")
            self.game_state, _ = self.turn_manager.next_turn(self.game_state)

    def announce_winner(self):
        winner = next(i for i, p in self.game_state.players.items() if p["influence_count"] > 0)
        self.display.display_game_over(winner)
     
