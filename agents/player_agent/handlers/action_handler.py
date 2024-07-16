import json

from agents.player_agent.handlers.base_handler import BaseHandler
from game.action import Action

class ActionHandler(BaseHandler):
    def _generate_context(self, game_state):
        roles_info = "\n".join([f"{role.name}: Actions: {role.actions}, Can block: {role.block_actions}" for role in self.player_agent.roles])
        strategies = "\n".join([strategy for role in self.player_agent.roles for strategy in role.get_strategies(game_state)])

        # Get a list of active players (players with influence > 0)
        active_players = [player_id for player_id, player_data in game_state.players.items() if player_data["influence_count"] > 0]

        system_message = """
        You are an AI player in a game of Coup. Your role is to make strategic decisions based on the current game state and your specific role.

        When deciding on an action, you need to choose the most strategic move based on the current game state and your roles.
        Always respond with a JSON object representing an Action, in the following format:
        {
            "type": "action_name",
            "target": null or player_id
            "rationale": "A brief explanation of why you chose this action"
        }

        Possible action types include:
        - "income": Take 1 coin from the treasury
        - "foreign_aid": Take 2 coins from the treasury (can be blocked by Duke)
        - "coup": Pay 7 coins and launch a coup against a target player
        - "tax": Take 3 coins from the treasury (Duke action)
        - "assassinate": Pay 3 coins and assassinate a target player (Assassin action)
        - "steal": Steal 2 coins from a target player (Captain action)
        - "exchange": Exchange cards with the Court deck (Ambassador action)

        IMPORTANT RULES:
        1. If you have 10 or more coins, you MUST choose the "coup" action and target another player. This is a mandatory rule of the game.
        2. You can only target players who still have influence (i.e., are still in the game).
        3. For actions that require a target (coup, assassinate, steal), you must choose a target from the list of active players.
        4. You can only choose "coup" if you have at least 7 coins.
        5. You can only choose "assassinate" if you have at least 3 coins.
        6. Always check your available coins before choosing an action.

        Here's an example of a game state and how to interpret it:

        {
          "players": {
            "0": {"influence_count": 2, "coins": 3},
            "1": {"influence_count": 1, "coins": 5},
            "2": {"influence_count": 0, "coins": 0},
            "3": {"influence_count": 2, "coins": 7}
          },
          "current_player": 1,
          "deck": ["Duke", "Assassin", "Captain", "Ambassador", "Contessa"],
        }

        In this example:
        - Players 0, 1, and 3 are still active in the game (influence_count > 0).
        - Player 2 has been eliminated (influence_count = 0).
        - The current player is Player 1.
        - Player 3 has the most coins (7).

        When choosing an action:
        - You can target Players 0, 1, or 3 for actions like coup, assassinate, or steal.
        - You should NOT target Player 2 for any action, as they are out of the game.
        - If you were Player 1 in this example and had the Assassin role, you could choose to assassinate Player 3 (who has the most coins) or Player 0.
        - You cannot choose coup unless you have at least 7 coins.
        - If you had 10 or more coins, you would be required to coup either Player 0 or Player 3 (not Player 2, as they're eliminated).

        Use this example to guide your interpretation of the actual game state provided.
        """

        user_message = f"""
        It's your turn to take an action. Here's your current status and the game state:

        Your player ID: {self.player_agent.player_id}
        Your roles: {[role.name for role in self.player_agent.roles]}
        Your coins: {self.player_agent.coins}

        Role details:
        {roles_info}

        Strategic considerations:
        {strategies}

        Current game state:
        {game_state.model_dump_json(indent=2)}

        Active players (players still in the game):
        {active_players}

        REMEMBER: 
        - If you have 10 or more coins, you MUST choose the "coup" action and target another player.
        - You can only target players who are still active in the game (listed above).
        - You can only choose "coup" if you have at least 7 coins.
        - You can only choose "assassinate" if you have at least 3 coins.
        - Always check your available coins before choosing an action.
        - Provide a brief rationale for your chosen action in the "rationale" field of the JSON object.

        Based on this information, please decide on the most strategic action to take.
        Provide your decision in the required JSON format representing an Action object.
        """

        return system_message, user_message

    def _parse_decision(self, decision):
        decision_dict = json.loads(decision)
        return Action(type=decision_dict["type"], target=decision_dict["target"], rationale=decision_dict["rationale"])