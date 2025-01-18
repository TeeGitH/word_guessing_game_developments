let gameActive = false;

function updateAttempts(count) {
    document.getElementById('attempts-count').textContent = count;
}

function startNewGame() {
    if (gameActive) {
        // If game is active, first reveal the answer
        fetch('/exit-game', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                addMessage(data.message, 'ai');
                clearMessages();
                startNewGameFlow();
            });
    } else {
        clearMessages();
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
            updateAttempts(data.attempts_made);
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

function clearMessages() {
    const chatContainer = document.getElementById('chat-container');
    chatContainer.innerHTML = ''; // Clear all messages
}

// Enable Enter key to submit
document.getElementById('guess-input').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        makeGuess();
    }
});

// Start game automatically when page loads
document.addEventListener('DOMContentLoaded', function() {
    startNewGame();
}); 