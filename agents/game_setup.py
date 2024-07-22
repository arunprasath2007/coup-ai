import random
from typing import Any, Dict
from agents.player_agent.player_agents import PlayerAgent
from game.game_state import GameState

from roles.base_role import Role
from roles.duke import Duke
from roles.captain import Captain
from roles.ambassador import Ambassador
from roles.assassin import Assassin
from roles.contessa import Contessa


class GameSetup:
    def __init__(self, num_players: int, llm_config: Dict[str, Any]):
        self.num_players = num_players
        self.llm_config = llm_config
        self.players = []
        self.deck = []

    def setup_players(self):
        role_types = [Duke, Captain, Ambassador, Assassin, Contessa]
        self.deck = [role() for role in role_types for _ in range(3)]  # 3 of each role
        random.shuffle(self.deck)

        for i in range(self.num_players):
            roles = [self.deck.pop(), self.deck.pop()]
            player = PlayerAgent(name=f"Player{i}", player_id=i, roles=roles, llm_config=self.llm_config)
            self.players.append(player)

    def create_initial_game_state(self) -> GameState:
        return GameState(
            players={i: {"influence_count": 2, "coins": 2} for i in range(self.num_players)},
            current_player=0,
            deck=[role.name for role in self.deck]
        )