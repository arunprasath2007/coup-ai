from abc import ABC, abstractmethod
from utils.llm_utils import LLMUtils

class BaseHandler(ABC):
    def __init__(self, player_agent, llm_config):
        self.player_agent = player_agent
        self.llm_config = llm_config

    def make_decision(self, game_state, **kwargs):
        system_message, user_message = self._generate_context(game_state, **kwargs)
        llm_response = LLMUtils.get_llm_response(system_message, user_message)
        return self._parse_decision(llm_response, **kwargs)

    @abstractmethod
    def _generate_context(self, game_state, **kwargs):
        pass

    @abstractmethod
    def _parse_decision(self, decision, **kwargs):
        pass