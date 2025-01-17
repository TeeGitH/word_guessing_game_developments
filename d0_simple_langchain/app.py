from flask import Flask, jsonify, render_template, request
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

# Game state
game_state = {
    'current_word': None,
    'guesses': [],
    'game_active': False,
    'attempts_made': 0,
    'max_attempts': 10,
    'previous_words': set()
}

def get_random_word():
    """Generate a random word using OpenAI API"""
    try:
        prompts = [
            "Generate a random common noun (object, animal, food, etc.) that would be fun to guess in a word game. Respond with just the word.",
            "Give me a simple word from one of these categories: fruits, animals, household items, or clothing. Respond with just the word.",
            "Provide a common English word that a child would know, suitable for a guessing game. Respond with just the word.",
            "Generate a random word from everyday life (could be food, object, animal, etc.). Keep it simple and respond with just the word."
        ]
        
        for _ in range(3):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a word generator for a word guessing game. Provide only a single word."},
                    {"role": "user", "content": random.choice(prompts)}
                ],
                max_tokens=50,
                temperature=0.9
            )
            
            word = response.choices[0].message.content.strip().lower()
            
            if word not in game_state['previous_words']:
                game_state['previous_words'].add(word)
                if len(game_state['previous_words']) > 20:
                    game_state['previous_words'].pop()
                return word
        
        game_state['previous_words'].clear()
        return word
    
    except Exception as e:
        print(f"Error getting word from OpenAI: {str(e)}")
        return None

def get_game_response(guess):
    """Get AI response for the player's guess"""
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
        7. If they're getting closer, encourage them without specifying which parts are correct"""),
        HumanMessage(content=f"""The target word is '{game_state['current_word']}'. 
        Player's guess: '{guess}'.
        Previous guesses: {game_state['guesses']}.
        Provide a hint following the strict rules above.""")
    ]
    
    response = chat_model.predict_messages(messages)
    return response.content

@app.route('/')
def home():
    """Render the game interface"""
    return render_template('index.html')

@app.route('/start-game', methods=['POST'])
def start_game():
    """Initialize a new game"""
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
    """Reveal the current word"""
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
    """End the current game"""
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
    """Process a player's guess"""
    if not game_state['game_active']:
        return jsonify({
            "message": "Please start a new game first!",
            "status": "error",
            "attempts_made": game_state['attempts_made']
        })

    guess = request.json.get('guess', '').lower().strip()
    game_state['attempts_made'] += 1
    
    if guess.lower() in ['i give up', 'give up', 'giveup']:
        game_state['game_active'] = False
        return jsonify({
            "message": f"The word was '{game_state['current_word']}'. Don't worry, try another round!",
            "status": "success",
            "game_over": True,
            "attempts_made": game_state['attempts_made']
        })

    game_state['guesses'].append(guess)

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
