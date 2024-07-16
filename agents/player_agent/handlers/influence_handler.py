import json
from agents.player_agent.handlers.base_handler import BaseHandler

class InfluenceHandler(BaseHandler):
    def _generate_context(self, game_state, **kwargs):
        player_id = self.player_agent.player_id
        roles = self.player_agent.roles
        
        system_message = """
        You are an AI player in a game of Coup. You must choose which influence (card) to lose.
        Consider the strategic value of each role and how it fits with your current game state and strategy.

        Roles in Coup:
        - Duke: Can take 3 coins as tax, blocks foreign aid
        - Assassin: Can pay 3 coins to assassinate another player, unless blocked by Contessa
        - Captain: Can steal 2 coins from another player, blocks stealing
        - Ambassador: Can exchange cards, blocks stealing
        - Contessa: Blocks assassination attempts

        Respond with a JSON object indicating the index of the card you want to discard, like this:
        {
            "discard_index": 0
        }
        """

        user_message = f"""
        You are Player {player_id} in the game of Coup.
        Your current coins: {game_state.players[player_id]['coins']}

        Your current roles:
        {', '.join(f"{i}: {role.name}" for i, role in enumerate(roles))}

        You must choose one influence to lose.

        Current game state:
        {game_state.model_dump_json(indent=2)}

        Based on this information, which influence do you want to discard? Provide your decision in the required JSON format.
        """

        return system_message, user_message

    def _parse_decision(self, decision, **kwargs):
        try:
            decision_dict = json.loads(decision)
            discard_index = decision_dict.get("discard_index", 0)
            if not isinstance(discard_index, int) or discard_index not in [0, 1]:
                raise ValueError("Invalid discard_index")
            return discard_index
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing discard decision: {e}")
            return 0  # Default to discarding the first card

    def make_decision(self, game_state, **kwargs):
        roles = self.player_agent.roles
        if len(roles) == 1:
            return 0  # If only one role left, return its index

        return super().make_decision(game_state, **kwargs)