import json
import autogen
from typing import List, Dict, Any, Tuple
from agents.player_agent.handlers.action_handler import ActionHandler
from agents.player_agent.handlers.exchange_handler import ExchangeHandler
from agents.player_agent.handlers.influence_handler import InfluenceHandler
from agents.player_agent.handlers.response_handler import ResponseHandler
from roles.base_role import Role
from game.game_state import GameState
from game.action import Action

class PlayerAgent(autogen.ConversableAgent):
    def __init__(self, name, player_id, roles, llm_config, **kwargs):
        super().__init__(name=name, llm_config=llm_config, **kwargs)
        self.player_id = player_id
        self.roles = roles
        self.coins = 2
        self.action_handler = ActionHandler(self, llm_config)
        self.response_handler = ResponseHandler(self, llm_config)
        self.exchange_handler = ExchangeHandler(self, llm_config)
        self.influence_handler = InfluenceHandler(self, llm_config)

    def generate_reply(self, messages, sender, **kwargs):
        last_message = messages[-1]['content']
        
        if "PLAYER_ACTION" in last_message:
            game_state = GameState.parse_raw(last_message.split("PLAYER_ACTION")[-1].strip())
            action = self.action_handler.make_decision(game_state)
            return f"ACTION {action.json()}"
        elif "RESPOND_TO_ACTION" in last_message:
            message_content = json.loads(last_message)
            game_state = GameState.parse_raw(message_content["game_state"])
            action = Action.parse_raw(message_content["action"])
            return self.response_handler.make_decision(game_state, action=action)
        
        return super().generate_reply(messages, sender, **kwargs)

    def choose_cards_for_exchange(self, game_state, available_cards, num_to_keep):
        return self.exchange_handler.make_decision(game_state=game_state, available_cards=available_cards, num_to_keep=num_to_keep)

    def choose_influence_to_lose(self, game_state: GameState) -> Role:
        chosen_index = self.influence_handler.make_decision(game_state)

        if chosen_index < 0 or chosen_index >= len(self.roles):
            chosen_index = 0

        discarded_role = self.roles.pop(chosen_index)
        return discarded_role
    
