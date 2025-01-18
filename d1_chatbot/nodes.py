from openai import OpenAI
import os
import random
from typing import List, Dict
from agent_state import GameState

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def get_random_word() -> str:
    """Generate a random word using OpenAI API."""
    prompts = [
        "Generate a random common noun (object, animal, food, etc.) that would be fun to guess in a word game. Respond with just the word.",
        "Give me a simple word from one of these categories: fruits, animals, household items, or clothing. Respond with just the word.",
        "Provide a common English word that a child would know, suitable for a guessing game. Respond with just the word.",
    ]
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a word generator for a word guessing game. Provide only a single word."},
            {"role": "user", "content": random.choice(prompts)}
        ],
        max_tokens=50,
        temperature=0.9
    )
    
    return response.choices[0].message.content.strip().lower()

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