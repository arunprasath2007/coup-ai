import json
import random
from actions.assassinate_handler import AssassinateHandler
from actions.coup_handler import CoupHandler
from actions.exchange_handler import ExchangeHandler
from actions.foreign_aid_handler import ForeignAidHandler
from actions.income_handler import IncomeHandler
from actions.steal_handler import StealHandler
from actions.tax_handler import TaxHandler
from display.console_display import ConsoleDisplay
from game.game_state import GameState
from utils.role_utils import RoleUtils

class GameStateManager:
    def __init__(self, player_agents):
        self.action_handlers = {
            "income": IncomeHandler(),
            "foreign_aid": ForeignAidHandler(),
            "exchange": ExchangeHandler(),
            "coup": CoupHandler(),
            "assassinate": AssassinateHandler(),
            "steal": StealHandler(),
            "tax": TaxHandler(),
        }
        self.player_agents = player_agents
        self.display = ConsoleDisplay()

    def apply_action(self, game_state: GameState, action: dict):
        action_type = action["type"].lower()
        player_id = action["player_id"]
        target_id = action.get("target")
        
        if action_type in self.action_handlers:
            handler = self.action_handlers[action_type]
            if action_type in ["coup", "assassinate", "steal"]:
                return handler.execute(game_state, player_id, target_id, self.player_agents[target_id], self.player_agents[player_id])
            else:
                return handler.execute(game_state, player_id, self.player_agents[player_id])
        else:
            raise ValueError(f"Unknown action type: {action_type}")

    def apply_challenge_result(self, game_state: GameState, challenge_result: dict, target_id: int=None) -> GameState:
        challenge_result = json.loads(challenge_result)
        
        challenger = challenge_result["challenger"]
        challenged = challenge_result["challenged"]
        original_action = challenge_result["original_action"]
        
        #todo: HACK SHOULD HAVE BEEN HANDLED AT THE CONTEXT LEVEL. NEED TO AVOID THIS
        if target_id is not None:
            original_action["target"] = target_id
            
        if challenger["loses_influence"]:
            #todo: HACK TO HANDLE DOUBLE INFLUENCE LOSS ESPECIALLY FOR CASES LIKE COUP AND ASSASINATE WHEN THE BLOCK FAILS. NEED TO FIND A BETTER WAY
            if original_action["type"] == "assassinate" and challenger["player_id"] == target_id:
                if game_state.players[challenger["player_id"]]["influence_count"] > 1:
                    game_state = self._lose_influence(game_state, challenger["player_id"])
            else:
                game_state = self._lose_influence(game_state, challenger["player_id"])
        
        if challenged["loses_influence"]:
            game_state = self._lose_influence(game_state, challenged["player_id"])
        
        if challenged["reveals_card"]:
            revealed_role = challenged["revealed_role"]
            player = self.player_agents[challenged["player_id"]]
            if game_state.players[challenged["player_id"]]["influence_count"] > 0 and any(role.name.lower() == revealed_role.lower() for role in player.roles):
                game_state = self._reveal_and_replace_card(game_state, challenged["player_id"], revealed_role)
        
        if original_action["proceeds"]:
            game_state = self.apply_action(game_state, original_action)
        
        return game_state
    
    def apply_block_result(self, game_state: GameState, block_result: dict, target_id: int=None) -> GameState:
        block_result = json.loads(block_result) 
        
        blocker = block_result["blocker"]
        blocked_player = block_result["blocked_player"]
        original_action = block_result["original_action"]
        
        #todo: HACK SHOULD HAVE BEEN HANDLED AT THE CONTEXT LEVEL. NEED TO AVOID THIS
        if target_id is not None:
            original_action["target"] = target_id

        if block_result["block_successful"]:
            self.display.display_conversation("GameMaster", f"Player {blocker['player_id']}'s block is successful. The {original_action['type']} action is canceled.")
            
            game_state = self._reveal_and_replace_card(game_state, blocker["player_id"], blocker["revealed_role"])
            
        else:
            self.display.display_conversation("GameMaster", f"Player {blocker['player_id']}'s block fails. The {original_action['type']} action proceeds.")
            
            #todo: HACK TO HANDLE DOUBLE INFLUENCE LOSS ESPECIALLY FOR CASES LIKE COUP AND ASSASINATE WHEN THE BLOCK FAILS. NEED TO FIND A BETTER WAY
            if original_action["type"] not in ["assassinate", "coup"] and not game_state.players[blocker["player_id"]]["influence_count"] == 1 and blocker["player_id"] == target_id:
                game_state = self._lose_influence(game_state, blocker["player_id"])
            
            game_state = self.apply_action(game_state, original_action)

        return game_state

    def _lose_influence(self, game_state: GameState, player_id: int):
        player_agent = self.player_agents[player_id]
        
        #TODO: HACK TO HANDLE CASE WHERE PLAYER HAS NO ROLES LEFT. Need to find a better way.
        if(len(player_agent.roles) == 0):
            return game_state
        
        discarded_role = player_agent.choose_influence_to_lose(game_state)
        
        game_state.players[player_id]["influence_count"] -= 1
        
        if game_state.players[player_id]["influence_count"] == 0:
            self.display.display_elimination(player_id)
        
        game_state.deck.append(discarded_role.name)
        
        return game_state

    def _reveal_and_replace_card(self, game_state: GameState, player_id: int, revealed_role: str):
        player_agent = self.player_agents[player_id]
        
        role_to_remove = next((role for role in player_agent.roles if role.name.lower() == revealed_role.lower()), None)
        
        if role_to_remove:
            player_agent.roles.remove(role_to_remove)
        
        game_state.deck.append(revealed_role)
        random.shuffle(game_state.deck)
        
        if game_state.deck:
            new_role = game_state.deck.pop(0)
            new_role = RoleUtils.create_role_from_name(new_role)
            
            player_agent.roles.append(new_role)
        
        return game_state