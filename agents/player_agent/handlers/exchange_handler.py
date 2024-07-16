import json
from agents.player_agent.handlers.base_handler import BaseHandler


class ExchangeHandler(BaseHandler):
    def _generate_context(self, game_state, **kwargs):
        available_cards = kwargs.get('available_cards', [])
        num_to_keep = kwargs.get('num_to_keep', 1)
        
        system_message = """
        You are an AI player in a game of Coup. Your task is to choose which cards to keep during an exchange action.
        Consider the strategic value of each role and how it fits with your current game state and strategy.

        Roles in Coup:
        - Duke: Can take 3 coins as tax, blocks foreign aid
        - Assassin: Can pay 3 coins to assassinate another player, unless blocked by Contessa
        - Captain: Can steal 2 coins from another player, blocks stealing
        - Ambassador: Can exchange cards, blocks stealing
        - Contessa: Blocks assassination attempts

        Respond with a JSON object listing the indices of the cards you want to keep, like this:
        {
            "chosen_indices": [0, 2]
        }
        """

        user_message = f"""
        You are Player {self.player_agent.player_id} in the game of Coup.
        Your current coins: {game_state.players[self.player_agent.player_id]['coins']}
        Your current influence count: {game_state.players[self.player_agent.player_id]['influence_count']}

        Available cards for exchange:
        {', '.join(f"{i}: {card.name}" for i, card in enumerate(available_cards))}

        You must choose {num_to_keep} card(s) to keep.

        Current game state:
        {game_state.model_dump_json(indent=2)}

        Based on this information, which card(s) do you want to keep? Provide your decision in the required JSON format.
        """

        return system_message, user_message

    def _parse_decision(self, decision, **kwargs):
        available_cards = kwargs.get('available_cards', [])
        num_to_keep = kwargs.get('num_to_keep', 1)
        
        try:
            decision_dict = json.loads(decision)
            chosen_indices = decision_dict.get("chosen_indices", [])
            if not isinstance(chosen_indices, list) or not all(isinstance(i, int) for i in chosen_indices):
                raise ValueError("Invalid chosen_indices format")
            return [available_cards[i] for i in chosen_indices if 0 <= i < len(available_cards)]
        except (json.JSONDecodeError, ValueError, IndexError) as e:
            print(f"Error parsing exchange decision: {e}")
            # Fallback: return the first num_to_keep cards
            return available_cards[:num_to_keep]