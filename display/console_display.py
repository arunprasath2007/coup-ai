import random
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from game.game_state import GameState
from game.action import Action
from pyfiglet import Figlet
from rich.align import Align

class ConsoleDisplay:
    def __init__(self):
        self.console = Console()

    def display_game_state(self, game_state):
        table = Table(title="Game of Coup: Houses & Holdings", show_header=True, header_style="bold magenta")
        table.add_column("Player", style="cyan", no_wrap=True)
        table.add_column("Influences", style="green")
        table.add_column("Coins", justify="right", style="yellow")

        for player_id, player in game_state.players.items():
            table.add_row(
                f"Player {player_id}",
                str(player['influence_count']),
                str(player['coins'])
            )

        panel = Panel(
            table,
            expand=False,
            border_style="blue",
            padding=(1, 1)
        )

        self.console.print("\n")  
        self.console.print(panel)
        self.console.print("\n")  
    
        
    def display_welcome_message(self):
        f = Figlet(font='slant')
        welcome_ascii = f.renderText('Welcome to Coup AI')
        
        welcome_text = Text(welcome_ascii, style="bold green")
        welcome_text.append("\nPreparing the battleground...", style="italic")
        
        aligned_text = Align.center(welcome_text)
        
        panel = Panel(
            aligned_text,
            expand=False,
            border_style="yellow",
            title="Coup AI",
            subtitle="Get ready to play!"
        )

        self.console.print("\n") 
        self.console.print(panel)
        self.console.print("\n") 


    def display_player_turn(self, player_id: int, action: Action):
        action_description = f"{action.type}"
        if action.target is not None:
            action_description += f" targeting Player {action.target}"

        action_text = Text(f"Player {player_id} takes action: ")
        action_text.append(action_description, style="bold")

        if action.rationale is not None:
            rationale_text = Text("\nDon't tell anyone, but my super-secret strategy is: ", style="italic")
            rationale_text.append(action.rationale, style="cyan")
            
            # Combine action_text and rationale_text
            action_text.append(rationale_text)

        panel = Panel(
            action_text,
            title=f"Player {player_id}'s Turn",
            border_style="blue",
            expand=False,
            padding=(1, 1)
        )
        self.console.print(panel)

    def display_challenge(self, challenger_id: int, challenged_id: int, action: str, result: bool):
        result_text = "succeeds" if result else "fails"
        color = "green" if result else "red"
        
        panel = Panel(
            f"Player {challenger_id} challenges Player {challenged_id}'s [bold]{action}[/bold]\n"
            f"The challenge {result_text}!",
            title="Challenge",
            border_style=color
        )
        self.console.print(panel)

    def display_game_over(self, winner_id: int):
        text = Text(f"Player {winner_id} wins the game!", style="bold yellow")
        panel = Panel(text, title="Game Over", border_style="green")
        self.console.print(panel)

    def display_conversation(self, speaker: str, message: str):
        self.console.print(f"[bold]{speaker}:[/bold] {message}")
        
    def display_elimination(self, player_id: int):
        elimination_messages = [
            "Looks like you've been... eliminated! *puts on sunglasses*",
            "Another one bites the dust! And by dust, we mean political intrigue.",
            "Your coup... just got coup'd!",
            "From power player to... well, just player. Better luck next revolution!",
            "Eliminated? Don't worry, there's always the sequel: 'Coup 2: Electric Boogaloo'",
            "Your political career was shorter than a TikTok video!",
            "You've been voted off the... oh wait, wrong game show.",
            "Time to join the 'Ex-Players Club'. We have cookies!",
            "Your influence has left the building. Elvis-style!",
            "Game over, man! Game over! (But seriously, thanks for playing!)"
        ]

        funny_message = random.choice(elimination_messages)

        elimination_text = Text()   
        elimination_text.append("Player ", style="bold")
        elimination_text.append(str(player_id), style="bold red")
        elimination_text.append(" has lost all influence and is ", style="bold")
        elimination_text.append("ELIMINATED", style="bold red blink")
        elimination_text.append("!", style="bold")
        elimination_text.append("\n\n")
        elimination_text.append(funny_message, style="italic cyan")

        panel = Panel(
            elimination_text,
            title="Player Eliminated",
            border_style="red",
            expand=False,
            padding=(1, 1)
        )
        self.console.print(panel)