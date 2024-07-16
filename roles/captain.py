import json
from typing import List
from game.game_state import GameState
from game.action import Action
from .base_role import Role
from utils.llm_utils import LLMUtils

class Captain(Role):
    name: str = "Captain"
    actions: List[str] = ["steal"]
    block_actions: List[str] = ["steal"]

    def get_strategies(self, game_state: GameState) -> List[str]:
        system_message = """
        You are an AI assistant helping a player with the Captain role in the game of Coup. Your task is to generate strategic advice based on the current game state.
        
        The Captain can perform the following:
        1. Steal: Take 2 coins from another player
        2. Block Stealing: Prevent another player from stealing coins from you
        
        Consider the following when generating strategies:
        - The player's current coin count and influence
        - Other players' coin counts and influences
        - Recent actions in the game
        - Potential bluffing opportunities
        - When to use the Captain's stealing ability and when to bluff as other roles
        - The balance between aggressive actions (stealing) and defensive moves (blocking steals)
        
        Provide a list of 3-5 strategic suggestions that are specific to the current game state.
        Your response should be a JSON object with a single key "strategies" containing an array of strings.
        Each string in the array should be a distinct strategy.
        """

        user_message = f"""
        Current game state:
        {game_state.model_dump_json(indent=2)}

        You are advising a player with the Captain role.

        Please provide a JSON object containing a list of 3-5 strategic suggestions for the player's next move, 
        considering both the use of Captain's stealing ability, blocking potential, and potential bluffs.

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
        You are an AI assistant helping a player with the Captain role in the game of Coup. Your task is to generate response strategies based on another player's action.
        
        The Captain can steal coins from other players and block stealing attempts.
        
        Consider the following when generating response strategies:
        - The type of action taken by the other player
        - The current game state
        - The potential risks and benefits of challenging or blocking the action
        - The possibility of bluffing
        - The balance between aggressive counteractions and defensive moves
        
        Provide a list of 2-3 potential response strategies.
        Your response should be a JSON object with a single key "strategies" containing an array of strings.
        Each string in the array should be a distinct strategy.
        """

        user_message = f"""
        Current game state:
        {game_state.model_dump_json(indent=2)}

        Action taken by another player:
        {action.model_dump_json(indent=2)}

        You are advising a player with the Captain role.

        Please provide a JSON object containing a list of 2-3 potential response strategies to this action, 
        considering both the use of Captain's abilities and potential bluffs.

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