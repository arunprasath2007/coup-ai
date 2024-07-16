import json
from typing import List
from game.game_state import GameState
from game.action import Action
from .base_role import Role
from utils.llm_utils import LLMUtils

class Duke(Role):
    name: str = "Duke"
    actions: List[str] = ["tax"]
    block_actions: List[str] = ["foreign_aid"]

    def get_strategies(self, game_state: GameState) -> List[str]:
        system_message = """
        You are an AI assistant helping a player with the Duke role in the game of Coup. Your task is to generate strategic advice based on the current game state.
        
        The Duke can perform the following actions:
        1. Tax: Take 3 coins from the treasury
        2. Block Foreign Aid: Prevent another player from taking 2 coins as foreign aid
        
        Consider the following when generating strategies:
        - The player's current coin count and influence
        - Other players' coin counts and influences
        - Recent actions in the game
        - Potential bluffing opportunities
        - When to use the Duke's abilities and when to bluff as other roles
        
        Provide a list of 3-5 strategic suggestions that are specific to the current game state.
        Your response should be a JSON object with a single key "strategies" containing an array of strings.
        Each string in the array should be a distinct strategy.
        """

        user_message = f"""
        Current game state:
        {game_state.model_dump_json(indent=2)}

        You are advising a player with the Duke role.

        Please provide a JSON object containing a list of 3-5 strategic suggestions for the player's next move, 
        considering both the use of Duke abilities and potential bluffs.

        Example format:
        {{
            "strategies": [
                "Strategy 1",
                "Strategy 2",
                "Strategy 3"
            ],
            "rationale": "Explanation for why these strategies are good"
        }}
        """

        response = LLMUtils.get_llm_response(system_message, user_message)
        
        try:
            strategies_json = json.loads(response)
            return strategies_json["strategies"]
        except json.JSONDecodeError:
            print(f"Error decoding JSON from LLM response: {response}")
            return ["Error generating strategies"]
        except KeyError:
            print(f"'strategies' key not found in LLM response: {response}")
            return ["Error generating strategies"]
        
    def get_response_strategies(self, game_state: GameState, action: Action) -> List[str]:
        system_message = """
        You are an AI assistant helping a player with the Duke role in the game of Coup. Your task is to generate response strategies based on another player's action.
        
        The Duke can block Foreign Aid actions.
        
        Consider the following when generating response strategies:
        - The type of action taken by the other player
        - The current game state
        - The potential risks and benefits of challenging or blocking the action
        - The possibility of bluffing
        
        Provide a list of 2-3 potential response strategies.
        Your response should be a JSON object with a single key "strategies" containing an array of strings.
        Each string in the array should be a distinct strategy.
        """

        user_message = f"""
        Current game state:
        {game_state.model_dump_json(indent=2)}

        Action taken by another player:
        {action.model_dump_json(indent=2)}

        You are advising a player with the Duke role.

        Please provide a JSON object containing a list of 2-3 potential response strategies to this action, 
        considering both the use of Duke abilities and potential bluffs.

        Example format:
        {{
            "strategies": [
                "Response Strategy 1",
                "Response Strategy 2"
            ],
            "rationale": "Explanation for why these strategies are good"
        }}
        """

        response = LLMUtils.get_llm_response(system_message, user_message)
        
        try:
            strategies_json = json.loads(response)
            return strategies_json["strategies"]
        except json.JSONDecodeError:
            print(f"Error decoding JSON from LLM response: {response}")
            return ["Error generating response strategies"]
        except KeyError:
            print(f"'strategies' key not found in LLM response: {response}")
            return ["Error generating response strategies"]