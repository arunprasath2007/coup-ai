from display.console_display import ConsoleDisplay
from agents.game_master_agent import GameMasterAgent

import os
from dotenv import load_dotenv

load_dotenv()

def main():
    llm_config={"config_list": [{"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")}]}

    display = ConsoleDisplay()
    display.display_welcome_message()
    
    game_master = GameMasterAgent(num_players=4, llm_config=llm_config)
    game_master.run_game()

if __name__ == "__main__":
    main()
