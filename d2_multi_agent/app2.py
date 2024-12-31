from typing import Dict, List, Optional, Any, TypedDict, Annotated
from operator import itemgetter
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
import os
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from flask import Flask, jsonify, render_template_string, request

# Load environment variables
load_dotenv()

# Define our state
class GameState(TypedDict):
    messages: List[BaseMessage]
    current_word: Optional[str]
    attempts: int
    game_status: str

def create_game_graph():
    # Initialize our LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Create the graph
    workflow = StateGraph(GameState)
    
    # Define the nodes
    def generate_word(state: GameState) -> GameState:
        """Generate a new word for the game"""
        # Implementation here
        return state
    
    def process_guess(state: GameState) -> GameState:
        """Process the player's guess"""
        # Implementation here
        return state
    
    def generate_hint(state: GameState) -> GameState:
        """Generate a hint for the player"""
        # Implementation here
        return state
    
    # Add nodes
    workflow.add_node("generate_word", generate_word)
    workflow.add_node("process_guess", process_guess)
    workflow.add_node("generate_hint", generate_hint)
    
    # Define conditional routing
    def router(state: GameState) -> str:
        if state["game_status"] == "ended":
            return END
        if state["messages"][-1].content == "hint":
            return "generate_hint"
        return "process_guess"
    
    # Add edges
    workflow.set_entry_point("generate_word")
    workflow.add_edge("generate_word", router)
    workflow.add_edge("process_guess", router)
    workflow.add_edge("generate_hint", router)
    
    # Compile the graph
    return workflow.compile()

# Initialize the game
def init_game() -> GameState:
    return {
        "messages": [],
        "current_word": None,
        "attempts": 0,
        "game_status": "ongoing"
    } 

# HTML template
GAME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Word Guessing Game v2</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .message {
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
        }
        .ai-message {
            background-color: #e3f2fd;
            margin-right: 20%;
        }
        .user-message {
            background-color: #f0f4c3;
            margin-left: 20%;
        }
        .game-stats {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .input-container {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        input[type="text"] {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
        }
        button {
            padding: 10px 20px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            background-color: #45a049;
        }
        .controls {
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <h1>Word Guessing Game v2</h1>
    <div class="game-stats">
        <div>Attempts: <span id="attempts">0</span>/10</div>
    </div>
    <div class="controls">
        <button onclick="startNewGame()">Start New Game</button>
        <button onclick="requestHint()">Get Hint</button>
        <button onclick="exitGame()">Exit Game</button>
    </div>
    <div class="chat-container" id="chat-container">
    </div>
    <div class="input-container">
        <input type="text" id="guess-input" placeholder="Enter your guess..." disabled>
        <button onclick="makeGuess()" id="guess-button" disabled>Submit Guess</button>
    </div>

    <script>
        let gameActive = false;

        function addMessage(message, type) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function updateAttempts(count) {
            document.getElementById('attempts').textContent = count;
        }

        function startNewGame() {
            fetch('/start-game', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'ai');
                    document.getElementById('guess-input').disabled = false;
                    document.getElementById('guess-button').disabled = false;
                    gameActive = true;
                    updateAttempts(0);
                });
        }

        function makeGuess() {
            const guessInput = document.getElementById('guess-input');
            const guess = guessInput.value.trim();
            
            if (!guess) return;

            addMessage(guess, 'user');
            guessInput.value = '';

            fetch('/make-guess', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ guess: guess })
            })
            .then(response => response.json())
            .then(data => {
                addMessage(data.message, 'ai');
                updateAttempts(data.attempts);
                if (data.game_over) {
                    gameActive = false;
                    document.getElementById('guess-input').disabled = true;
                    document.getElementById('guess-button').disabled = true;
                }
            });
        }

        function requestHint() {
            if (!gameActive) return;
            
            fetch('/get-hint', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'ai');
                });
        }

        function exitGame() {
            fetch('/exit-game', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'ai');
                    gameActive = false;
                    document.getElementById('guess-input').disabled = true;
                    document.getElementById('guess-button').disabled = true;
                });
        }

        // Enable Enter key to submit
        document.getElementById('guess-input').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                makeGuess();
            }
        });
    </script>
</body>
</html>
'''

# Flask app
app = Flask(__name__)

# Game instance
game_instance = None

@app.route('/')
def home():
    return render_template_string(GAME_PAGE)

@app.route('/start-game', methods=['POST'])
def start_game():
    global game_instance
    state = init_game()
    state["messages"].append(HumanMessage(content="Let's start the game!"))
    game_instance = create_game_graph()
    result = game_instance.invoke(state)
    
    return jsonify({
        "message": "I've picked a word! Start guessing!",
        "status": "success"
    })

@app.route('/make-guess', methods=['POST'])
def make_guess():
    guess = request.json.get('guess', '').lower().strip()
    state = game_instance.get_state()
    state["messages"].append(HumanMessage(content=guess))
    result = game_instance.invoke(state)
    
    return jsonify({
        "message": result["messages"][-1].content,
        "attempts": state["attempts"],
        "game_over": state["game_status"] == "ended",
        "status": "success"
    })

@app.route('/get-hint', methods=['POST'])
def get_hint():
    state = game_instance.get_state()
    state["messages"].append(HumanMessage(content="hint"))
    result = game_instance.invoke(state)
    
    return jsonify({
        "message": result["messages"][-1].content,
        "status": "success"
    })

@app.route('/exit-game', methods=['POST'])
def exit_game():
    state = game_instance.get_state()
    return jsonify({
        "message": f"Thanks for playing! The word was '{state['current_word']}'",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(debug=True) 