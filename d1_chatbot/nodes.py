from openai import OpenAI
import os
import random
from typing import List, Dict
from agent_state import GameState

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_random_word() -> str:
    """Return a random word for the game."""
    # For now, return a fixed word. Later we can expand this.
    return "python"

def chatbot_node(state: GameState) -> Dict:
    """
    Chatbot node that handles game initialization, interactions, and decisions.
    Acts as an LLM that manages the game flow and player interactions.
    """
    # If game not initialized, set it up
    if not state.get("current_word"):
        return {
            "current_word": get_random_word(),
            "game_active": True,
            "messages": [{"role": "assistant", "content": "Hi! I'm your word guessing game host. I've picked a word. Try to guess it!"}]
        }
    
    # Get the last user message
    last_message = state["messages"][-1]
    
    # If it's a user message, process it
    if last_message["role"] == "user":
        guess = last_message["content"].strip().lower()
        word = state["current_word"].lower()
        
        # Generate appropriate response based on the guess
        if guess == word:
            state["messages"].append({
                "role": "assistant",
                "content": f"Congratulations! You've guessed the word '{word}' correctly!"
            })
            state["game_active"] = False
        else:
            # Here we could add more sophisticated hint generation
            hint = "The word is shorter" if len(guess) > len(word) else "The word is longer" if len(guess) < len(word) else "Same length, but not correct"
            state["messages"].append({
                "role": "assistant",
                "content": f"Not quite right. Here's a hint: {hint}"
            })
    
    return state

def process_guess(state: GameState) -> Dict:
    """Process chat messages and return response."""
    messages = [
        {"role": "system", "content": "You are a friendly word guessing game host. Never reveal the word unless the player explicitly says 'I give up'. Provide clever hints about the word's category, size, or common uses without directly confirming if any part of the guess is correct."},
        *state["messages"][-5:]  # Keep last 5 messages for context
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )
    
    return {
        "messages": [{"role": "assistant", "content": response.choices[0].message.content}],
        "attempts": state["attempts"] + 1
    }

def check_game_status(state: GameState) -> str:
    """Check game status and determine next action."""
    if not state["game_active"]:
        return "END"
        
    if state["attempts"] >= state["max_attempts"]:
        return "END"
        
    last_message = state["messages"][-1]["content"].lower()
    if "quit" in last_message or "exit" in last_message or "i give up" in last_message:
        return "END"
        
    if state["current_word"] and last_message == state["current_word"]:
        return "END"
        
    return "CONTINUE" 