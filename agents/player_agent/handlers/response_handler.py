import json
from agents.player_agent.handlers.base_handler import BaseHandler

class ResponseHandler(BaseHandler):
    def _generate_context(self, game_state, action):
        roles_info = "\n".join([f"{role.name}: Actions: {role.actions}, Can block: {role.block_actions}" for role in self.player_agent.roles])
        strategies = "\n".join([strategy for role in self.player_agent.roles for strategy in role.get_response_strategies(game_state=game_state, action=action)])

        system_message = """
        You are an AI player in a game of Coup. Your role is to make strategic decisions based on the game state and actions of other players.

        When responding to an action, you need to decide whether to challenge, block, or allow the action.
        Always respond with a JSON object in the following format:
        {
            "response": "CHALLENGE" or "BLOCK" or "ALLOW"
        }

        For example:
        - {"response": "CHALLENGE"} if you want to challenge the action.
        - {"response": "BLOCK"} if you want to block the action (only if your roles allow it).
        - {"response": "ALLOW"} if you want to allow the action to proceed.
        """

        user_message = f"""
        An action has been taken by another player. Here are your details and the action details:

        Your player ID: {self.player_agent.player_id}
        Your roles: {[role.name for role in self.player_agent.roles]}
        Your coins: {self.player_agent.coins}

        Role details:
        {roles_info}

        Strategic considerations for responding:
        {strategies}

        Current game state:
        {game_state.model_dump_json(indent=2)}

        Action taken by another player:
        {action.json()}

        Based on this information, please decide whether to challenge, block, or allow the action.
        Provide your decision in the required JSON format.
        """

        return system_message, user_message

    def _parse_decision(self, decision, **kwargs):
        try:
            decision_dict = json.loads(decision)
            decision = decision_dict.get('response', '').strip().upper()
        except json.JSONDecodeError:
            decision = decision.strip().upper()

        return decision if decision in ["CHALLENGE", "BLOCK", "ALLOW"] else "ALLOW"