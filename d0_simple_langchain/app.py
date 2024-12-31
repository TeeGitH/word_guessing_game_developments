from flask import Flask, jsonify, render_template_string, request
from dotenv import load_dotenv
import os
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import random

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Initialize LangChain chat model
chat_model = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.7,
    openai_api_key=os.getenv('OPENAI_API_KEY')
)

# Game state (in a real application, you'd want to use a proper database)
game_state = {
    'current_word': None,
    'guesses': [],
    'game_active': False,
    'attempts_made': 0,
    'max_attempts': 10,
    'previous_words': set()  # Keep track of recently used words
}

# HTML template for the game interface
GAME_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Word Guessing Game</title>
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
        .game-stats {
            background-color: #e8f5e9;
            padding: 10px;
            border-radius: 5px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .attempts-counter {
            font-size: 1.1em;
            color: #2e7d32;
        }
        .button-group {
            display: flex;
            gap: 10px;
        }
        .exit-button {
            background-color: #f44336;
        }
        .exit-button:hover {
            background-color: #d32f2f;
        }
        .restart-button {
            background-color: #ff9800;
        }
        .restart-button:hover {
            background-color: #f57c00;
        }
    </style>
</head>
<body>
    <h1>Word Guessing Game</h1>
    <div class="game-stats">
        <div class="attempts-counter">
            Attempts Made: <span id="attempts-count">0</span>/10
        </div>
        <div class="button-group">
            <button onclick="startNewGame()" class="restart-button">Restart Game</button>
            <button onclick="exitGame()" class="exit-button">Exit Game</button>
        </div>
    </div>
    <div class="chat-container" id="chat-container">
        <!-- Messages will appear here -->
    </div>
    <div class="input-container">
        <input type="text" id="guess-input" placeholder="Enter your guess..." disabled>
        <button onclick="makeGuess()" id="guess-button" disabled>Submit Guess</button>
    </div>

    <script>
        let gameActive = false;

        function updateAttempts(count) {
            document.getElementById('attempts-count').textContent = count;
        }

        function startNewGame() {
            if (gameActive) {
                // If game is active, first reveal the answer
                fetch('/reveal-word', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        addMessage(data.message, 'ai');
                        startNewGameFlow();
                    });
            } else {
                startNewGameFlow();
            }
        }

        function startNewGameFlow() {
            fetch('/start-game', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'ai');
                    document.getElementById('guess-input').disabled = false;
                    document.getElementById('guess-button').disabled = false;
                    updateAttempts(0);
                    gameActive = true;
                });
        }

        function exitGame() {
            fetch('/exit-game', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    addMessage(data.message, 'ai');
                    document.getElementById('guess-input').disabled = true;
                    document.getElementById('guess-button').disabled = true;
                    gameActive = false;
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
                updateAttempts(data.attempts_made);
                if (data.game_over) {
                    document.getElementById('guess-input').disabled = true;
                    document.getElementById('guess-button').disabled = true;
                    gameActive = false;
                }
            });
        }

        function addMessage(message, type) {
            const chatContainer = document.getElementById('chat-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = message;
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
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

def get_random_word():
    try:
        # List of different prompts to get more variety
        prompts = [
            "Generate a random common noun (object, animal, food, etc.) that would be fun to guess in a word game. Respond with just the word.",
            "Give me a simple word from one of these categories: fruits, animals, household items, or clothing. Respond with just the word.",
            "Provide a common English word that a child would know, suitable for a guessing game. Respond with just the word.",
            "Generate a random word from everyday life (could be food, object, animal, etc.). Keep it simple and respond with just the word."
        ]
        
        # Try up to 3 times to get a unique word
        for _ in range(3):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a word generator for a word guessing game. Provide only a single word."
                    },
                    {
                        "role": "user",
                        "content": random.choice(prompts)
                    }
                ],
                max_tokens=50,
                temperature=0.9  # Increased temperature for more randomness
            )
            
            word = response.choices[0].message.content.strip().lower()
            
            # Check if word is unique (not used in recent games)
            if word not in game_state['previous_words']:
                # Add to previous words, keeping only the last 20 words
                game_state['previous_words'].add(word)
                if len(game_state['previous_words']) > 20:
                    game_state['previous_words'].pop()
                return word
        
        # If we couldn't get a unique word after 3 tries, clear the previous words and return the last generated word
        game_state['previous_words'].clear()
        return word
    
    except Exception as e:
        print(f"Error getting word from OpenAI: {str(e)}")
        return None

def get_game_response(guess):
    messages = [
        SystemMessage(content="""You are a word guessing game assistant. Follow these strict rules:
        1. NEVER reveal the target word under any circumstances, unless the player says "I give up"
        2. NEVER use the target word in your responses, even as part of another word
        3. NEVER directly confirm if any part of the guess is correct
        4. Instead, provide clever hints about:
           - General category (animal, object, food, etc.)
           - Size comparison (bigger, smaller)
           - Common uses or characteristics
           - First letter (only if player is struggling after multiple guesses)
        5. Keep responses brief, encouraging, and fun
        6. If the guess is completely wrong, guide them in a new direction
        7. If they're getting closer, encourage them without specifying which parts are correct
        
        Example good responses:
        - "Think of something much larger than that!"
        - "This creature is known for its impressive size"
        - "You're looking for something that lives on land"
        
        Example bad responses (never do these):
        - "The word contains the letter 'e'" (too direct)
        - "It's like your guess but bigger" (too specific)
        - "It starts with 'ele'" (reveals part of word)"""),
        HumanMessage(content=f"""The target word is '{game_state['current_word']}'. 
        Player's guess: '{guess}'.
        Previous guesses: {game_state['guesses']}.
        Provide a hint following the strict rules above.""")
    ]
    
    response = chat_model.predict_messages(messages)
    return response.content

@app.route('/')
def home():
    return render_template_string(GAME_PAGE)

@app.route('/start-game', methods=['POST'])
def start_game():
    # Clear the game state
    game_state['current_word'] = get_random_word()
    game_state['guesses'] = []
    game_state['game_active'] = True
    game_state['attempts_made'] = 0
    return jsonify({
        "message": "I've picked a word! Start guessing!",
        "status": "success"
    })

@app.route('/reveal-word', methods=['POST'])
def reveal_word():
    if game_state['current_word']:
        return jsonify({
            "message": f"The word was '{game_state['current_word']}'.",
            "status": "success"
        })
    return jsonify({
        "message": "No word to reveal.",
        "status": "error"
    })

@app.route('/exit-game', methods=['POST'])
def exit_game():
    if game_state['current_word']:
        word = game_state['current_word']
        game_state['current_word'] = None
        game_state['guesses'] = []
        game_state['game_active'] = False
        game_state['attempts_made'] = 0
        return jsonify({
            "message": f"Thanks for playing! The word was '{word}'. Goodbye!",
            "status": "success"
        })
    return jsonify({
        "message": "Thanks for playing! Goodbye!",
        "status": "success"
    })

@app.route('/make-guess', methods=['POST'])
def make_guess():
    if not game_state['game_active']:
        return jsonify({
            "message": "Please start a new game first!",
            "status": "error",
            "attempts_made": game_state['attempts_made']
        })

    guess = request.json.get('guess', '').lower().strip()
    game_state['attempts_made'] += 1
    
    # Handle "give up" case
    if guess.lower() in ['i give up', 'give up', 'giveup']:
        game_state['game_active'] = False
        return jsonify({
            "message": f"The word was '{game_state['current_word']}'. Don't worry, try another round!",
            "status": "success",
            "game_over": True,
            "attempts_made": game_state['attempts_made']
        })

    game_state['guesses'].append(guess)

    # Check if max attempts reached
    if game_state['attempts_made'] >= game_state['max_attempts']:
        game_state['game_active'] = False
        return jsonify({
            "message": f"Game Over! You've reached {game_state['max_attempts']} attempts. The word was '{game_state['current_word']}'.",
            "status": "success",
            "game_over": True,
            "attempts_made": game_state['attempts_made']
        })

    if guess == game_state['current_word']:
        game_state['game_active'] = False
        return jsonify({
            "message": f"Congratulations! You've won! The word was '{game_state['current_word']}'!",
            "status": "success",
            "game_over": True,
            "attempts_made": game_state['attempts_made']
        })

    response = get_game_response(guess)
    return jsonify({
        "message": response,
        "status": "success",
        "game_over": False,
        "attempts_made": game_state['attempts_made']
    })

if __name__ == '__main__':
    app.run(debug=True)
