from typing import TypedDict, List, Optional

class GameState(TypedDict):
    """State definition for the word guessing game."""
    messages: List[dict]  # Chat history
    attempts: int  # Number of attempts made
    current_word: Optional[str]  # The word to guess
    game_active: bool  # Whether the game is currently active
    max_attempts: int  # Maximum allowed attempts

def create_initial_state() -> GameState:
    """Create initial game state."""
    return {
        "messages": [],
        "attempts": 0,
        "current_word": None,
        "game_active": False,
        "max_attempts": 10
    }

def update_state(state: GameState, updates: dict) -> GameState:
    """Update game state with new values."""
    return {**state, **updates} 