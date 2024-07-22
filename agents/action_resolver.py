import json
import random
from typing import Any, Dict, List, Tuple
from agents.player_agent.player_agents import PlayerAgent
from display.console_display import ConsoleDisplay
from game.action import Action
from game.game_state import GameState
from game.state_manager import GameStateManager

from roles.base_role import Role
from roles.duke import Duke
from roles.captain import Captain
from roles.ambassador import Ambassador
from roles.assassin import Assassin
from roles.contessa import Contessa
from utils.llm_utils import LLMUtils
from utils.role_utils import RoleUtils

class ActionResolver:
    def __init__(self, game_state_manager: GameStateManager, display: ConsoleDisplay, initiate_chat, llm_config):
        self.game_state_manager = game_state_manager
        self.display = display
        self.initiate_chat = initiate_chat
        self.llm_config = llm_config

    def resolve_action(self, action: Action, game_state: GameState, players: List[PlayerAgent]) -> GameState:
        current_player_id = game_state.current_player
        current_player = players[current_player_id]
    
        if self.is_action_challengeable(action) or self.is_action_blockable(action):
            responses = self.get_player_responses(action, current_player_id, game_state, players)
            game_state = self.process_player_responses(responses, action, current_player_id, game_state, players)
        elif action.type == "coup":
            action_dict = { "type": action.type, "player_id": current_player_id, "target": action.target }
            game_state = self.game_state_manager.apply_action(game_state, action_dict)
        else:
            action_dict = { "type": action.type, "player_id": current_player_id }
            game_state = self.game_state_manager.apply_action(game_state, action_dict)
        
        return game_state

    def get_player_responses(self, action: Action, current_player_id: int, game_state: GameState, players: List[PlayerAgent]) -> Dict[int, str]:
        responses = {}
        for player_id, player in enumerate(players):
            if player_id != current_player_id and game_state.players[player_id]["influence_count"] > 0:
                self.display.display_conversation("GameMaster", f"Asking Player {player_id} to respond")
                
                response = self.initiate_chat(
                    recipient=player,
                    message=json.dumps({
                                "type": "RESPOND_TO_ACTION",
                                "game_state": game_state.model_dump_json(),
                                "action": action.json(),
                                "is_challengeable": self.is_action_challengeable(action),
                                "is_blockable": self.is_action_blockable(action)
                            }),
                    silent=True,
                    config=self.llm_config,
                    max_turns=1
                )
                
                self.display.display_conversation("GameMaster", f"Player {player_id} responded")
                responses[player_id] = response.summary if response and response.summary else "NO_RESPONSE"
        return responses

    def process_player_responses(self, responses: Dict[int, str], action: Action, current_player_id: int, game_state: GameState, players: List[PlayerAgent]) -> GameState:
        challenges = []
        blocks = []
        for player_id, response in responses.items():
            if response.startswith("CHALLENGE") and self.is_action_challengeable(action):
                challenges.append(player_id)
            elif response.startswith("BLOCK") and self.is_action_blockable(action):
                blocks.append(player_id)
        
        if challenges:
            self.display.display_conversation("GameMaster", f"Player {challenges[0]} challenges Player {current_player_id}'s action.")
            game_state = self.resolve_challenge(challenges[0], current_player_id, action, players, game_state)
        elif blocks:
            self.display.display_conversation("GameMaster", f"Player {blocks[0]} blocks Player {current_player_id}'s action.")
            game_state = self.resolve_block(blocks[0], current_player_id, action, players, game_state)
        else: 
            self.display.display_conversation("GameMaster", f"Player {current_player_id}'s action is allowed to proceed by all players.")
            action_dict = { "type": action.type, "player_id": current_player_id, "target": action.target }
            game_state = self.game_state_manager.apply_action(game_state, action_dict)
            
        return game_state

    def is_action_challengeable(self, action: Action) -> bool:
        return action.type in ["tax", "assassinate", "steal", "exchange"]

    def is_action_blockable(self, action: Action) -> bool:
        return action.type in ["foreign_aid", "assassinate", "steal"]

    def resolve_challenge(self, challenger_id: int, challenged_id: int, action: Action, players: List[PlayerAgent], game_state: GameState) -> GameState:
        challenged_player = players[challenged_id]
        challenger_player = players[challenger_id]

        # Get the LLM's decision
        system_message, user_message = self._generate_challenge_context(challenger_id, challenged_id, action, players)
        llm_decision = LLMUtils.get_llm_response(system_message, user_message)
        
        rationale = json.loads(llm_decision)["rationale"]
        self.display.display_conversation("GameMaster", rationale) 

        # Parse the LLM's decision
        challenge_result = self._parse_challenge_decision(llm_decision, game_state)
        
        # Check if action.target exists and pass it to apply_block_result if it does
        target_id = action.target if hasattr(action, 'target') else None

        # Apply the results of the challenge
        game_state = self.game_state_manager.apply_challenge_result(game_state, challenge_result, target_id)
        
        return game_state
        
    def _generate_challenge_context(self, challenger_id: int, challenged_id: int, action: Action, players: List[PlayerAgent]) -> Tuple[str, str]:
        challenged_player = players[challenged_id]
        challenger_player = players[challenger_id]

        # Get role information
        role_info = RoleUtils.get_role_info()

        system_message = f"""
        You are the AI GameMaster for a game of Coup. Your role is to resolve challenges that occur during the game.

        Roles and their actions:
        {role_info}

        When a challenge occurs, you need to:
        1. Determine if the challenged action can be performed by any of the challenged player's roles.
        2. Decide the outcome of the challenge based on whether the challenged player has the required role.
        3. Provide a rationale for your decision.

        Always respond with a JSON object in the following format:
        {{
            "winner_id": player_id,
            "rationale": "Your explanation here on how you arrived at the winner"
        }}
        """

        user_message = f"""
        A challenge has occurred in the game. Here are the details:

        Challenge Details:
        - Challenger: Player {challenger_id}
        - Challenger's Roles: {', '.join(role.name for role in challenger_player.roles)}
        - Challenged: Player {challenged_id}
        - Challenged's Roles: {', '.join(role.name for role in challenged_player.roles)}
        - Challenged Action: {action.type}

        Please resolve this challenge and provide your decision in the required JSON format.
        """

        return system_message, user_message
    
    def _parse_challenge_decision(self, challenge_result: dict, game_state: GameState) -> str:
        system_message, user_message = self._generate_post_challenge_context(challenge_result, game_state)
        
        challenge_output = LLMUtils.get_llm_response(system_message, user_message)
        return challenge_output
    
    def _generate_post_challenge_context(self, challenge_result: dict, game_state: GameState) -> Tuple[str, str]:
        system_message = """
        You are the AI GameMaster for Coup. Your role is to determine the outcomes and necessary actions after a challenge has been resolved.

        Rules for resolving challenges:
        1. If the challenged player has the claimed card (challenge fails):
        - The challenger loses one influence (discards a card).
        - The challenged player reveals their claimed role card, shuffles it back into the deck, and draws a new card.
        - The original action proceeds as intended.
        2. If the challenged player doesn't have the claimed card (challenge succeeds):
        - The challenged player loses one influence (discards a card).
        - The original action is canceled.

        Respond with a JSON object detailing the outcomes and required actions:
        {
            "challenger": {
                "player_id": int,
                "loses_influence": boolean
            },
            "challenged": {
                "player_id": int,
                "loses_influence": boolean,
                "reveals_card": boolean,
                "revealed_role": string,
                "draws_new_card": boolean
            },
            "original_action": {
                "proceeds": boolean,
                "type": string,
                "player_id": int
            }
        }
        """

        user_message = f"""
        A challenge has been resolved. Here are the details:

        Challenge result:
        {json.dumps(challenge_result, indent=2)}

        Current game state:
        {game_state.model_dump_json(indent=2)}

        Based on this information and the rules of Coup, determine the outcomes and required actions.
        Provide your decision in the required JSON format.
        """

        return system_message, user_message
        
    
    def resolve_block(self, blocker_id: int, blocked_id: int, action: Action, players: List[PlayerAgent], game_state: GameState):
        self.display.display_conversation("GameMaster", f"Player {blocker_id} attempts to block Player {blocked_id}'s {action.type} action.")

        # Get the LLM's decision on the block
        system_message, user_message = self._generate_block_context(blocker_id, blocked_id, action, players, game_state)
        llm_decision = LLMUtils.get_llm_response(system_message, user_message)
        
        if(action.type == "assassinate"):
            print(f"action: {action}")
        
        # Check if action.target exists and pass it to apply_block_result if it does
        target_id = action.target if hasattr(action, 'target') else None
        
        game_state = self.game_state_manager.apply_block_result(game_state, llm_decision, target_id)
        return game_state

    def _generate_block_context(self, blocker_id: int, blocked_id: int, action: Action, players: List[PlayerAgent], game_state: GameState) -> Tuple[str, str]:
        blocker_player = players[blocker_id]
        blocked_player = players[blocked_id]

        system_message = """
        You are the AI GameMaster for a game of Coup. Your role is to resolve blocks that occur during the game.

        Block Rules in Coup:
        1. Foreign Aid can be blocked by the Duke.
        2. Stealing can be blocked by the Captain or Ambassador.
        3. Assassination can be blocked by the Contessa.

        When a block occurs, you need to:
        1. Determine if the blocking player claims to have a role that can block the action.
        2. Check if the blocking player actually has the role they're claiming.
        3. Decide the outcome of the block based on the game rules, claimed roles, and actual roles.
        4. If the block is successful, specify the exact role used for blocking in the 'revealed_role' field.
        5. Provide a rationale for your decision, including whether the block was successful and if the blocker was bluffing.

        Always respond with a JSON object in the following format:
        {
            "blocker": {
                "player_id": int,
                "revealed_role": string  // Must be specified if block is successful, use the exact role used for blocking
            },
            "blocked_player": {
                "player_id": int
            },
            "original_action": {
                "proceeds": boolean,
                "type": string,
                "player_id": int
            },
            "block_successful": boolean,
            "rationale": string
        }

        IMPORTANT: If the block is successful, you MUST specify the exact role used for blocking in the 'revealed_role' field.
        """

        user_message = f"""
        A block has occurred in the game. Here are the details:

        Block Details:
        - Blocker: Player {blocker_id}
        - Blocker's Claimed Role for this block: {', '.join(RoleUtils.get_claimed_role_for_block(action.type))}
        - Blocker's Actual Roles: {', '.join(role.name for role in blocker_player.roles)}
        - Blocked Player: Player {blocked_id}
        - Blocked Action: {action.type}

        Action being blocked:
        {action.model_dump_json(indent=2)}

        Game state:
        {game_state.model_dump_json(indent=2)}

        Please resolve this block and provide your decision in the required JSON format.
        Consider the block rules, the claimed role for the block, and the blocker's actual roles.
        Determine if the block is successful and if the blocker is bluffing.

        Remember: If the block is successful, you MUST specify the exact role used for blocking in the 'revealed_role' field.
        This should be one of the roles that can legally block this action, and preferably one that the blocker actually has.
        """

        return system_message, user_message

    def _parse_block_decision(self, decision: str) -> dict:
        try:
            block_result = json.loads(decision)
            required_keys = ["block_successful", "rationale"]
            if not all(key in block_result for key in required_keys):
                raise ValueError("Invalid block decision format")
            return block_result
        except (json.JSONDecodeError, ValueError) as e:
            self.display.display_conversation("GameMaster", f"Error parsing block decision: {e}")
            return {
                "block_successful": False,
                "rationale": "Error in decision parsing. Block fails by default."
            }
