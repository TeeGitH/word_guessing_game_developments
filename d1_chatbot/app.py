from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv
import os
from pathlib import Path
from .agent_state import create_initial_state, update_state
from .graph_setup import create_game_graph

# Get the root directory (parent of d1_chatbot)
root_dir = Path(__file__).parent.parent

# Load environment variables from root directory
load_dotenv(root_dir / '.env')

# Initialize Flask app
app = Flask(__name__)

# Initialize game graph
game_graph = create_game_graph()

# Global game state
game_state = create_initial_state()

@app.route('/')
def home():
    """Render the game interface."""
    return render_template('index.html')

@app.route('/start-game', methods=['POST'])
def start_game():
    """Initialize a new game."""
    global game_state
    game_state = create_initial_state()
    
    # Run the graph from start node
    result = game_graph.invoke(game_state)
    game_state = update_state(game_state, result)
    
    return jsonify({
        "message": result["messages"][-1]["content"],
        "status": "success",
        "attempts_made": game_state["attempts"]
    })

@app.route('/make-guess', methods=['POST'])
def make_guess():
    """Process a player's guess."""
    global game_state
    
    if not game_state["game_active"]:
        return jsonify({
            "message": "Please start a new game first!",
            "status": "error",
            "attempts_made": game_state["attempts"]
        })
    
    guess = request.json.get('guess', '').lower().strip()
    game_state["messages"].append({"role": "user", "content": guess})
    
    # Run the graph
    result = game_graph.invoke(game_state)
    game_state = update_state(game_state, result)
    
    # Check for game end conditions
    game_over = False
    if guess == game_state["current_word"]:
        message = f"Congratulations! You've won! The word was '{game_state['current_word']}'!"
        game_state["game_active"] = False
        game_over = True
    elif game_state["attempts"] >= game_state["max_attempts"]:
        message = f"Game Over! You've reached {game_state['max_attempts']} attempts. The word was '{game_state['current_word']}'."
        game_state["game_active"] = False
        game_over = True
    elif guess.lower() in ['i give up', 'give up', 'giveup']:
        message = f"The word was '{game_state['current_word']}'. Don't worry, try another round!"
        game_state["game_active"] = False
        game_over = True
    else:
        message = result["messages"][-1]["content"]
    
    return jsonify({
        "message": message,
        "status": "success",
        "game_over": game_over,
        "attempts_made": game_state["attempts"]
    })

@app.route('/exit-game', methods=['POST'])
def exit_game():
    """End the current game."""
    global game_state
    word = game_state["current_word"]
    game_state = create_initial_state()
    
    return jsonify({
        "message": f"Thanks for playing! The word was '{word}'. Goodbye!" if word else "Thanks for playing! Goodbye!",
        "status": "success"
    })

if __name__ == '__main__':
    app.run(debug=True) 