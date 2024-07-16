from utils.role_utils import RoleUtils
from .base_handler import ActionHandler
from game.game_state import GameState
from agents.player_agent.player_agents import PlayerAgent

class ExchangeHandler(ActionHandler):
    def execute(self, game_state: GameState, player_id: int, player_agent: PlayerAgent):
        player_influence = game_state.players[player_id]["influence_count"]
        
        # Draw two cards from the deck
        drawn_cards = game_state.deck[:2]
        game_state.deck = game_state.deck[2:]
        
        # Let the player choose which cards to keep
        player_roles = player_agent.roles
        all_available_cards = player_roles +  [RoleUtils.create_role_from_name(card) for card in drawn_cards]
        chosen_cards = player_agent.choose_cards_for_exchange(game_state=game_state, available_cards=all_available_cards, num_to_keep=player_influence)
        
        # Update player's roles and return unchosen cards to the deck
        player_agent.roles = chosen_cards
        returned_cards = [card for card in all_available_cards if card not in chosen_cards]
        # game_state.deck.extend(returned_cards)
        game_state.deck.extend([card.name for card in returned_cards])
        
        return game_state