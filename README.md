# Word Guessing Game Development

A progressive development of a word guessing game, showcasing different architectural approaches and improvements.

## Project Structure

### d0_simple_langchain/
Initial version using basic LangChain integration
- Simple word generation
- Basic hint system
- Flask web interface
- File: `app.py`

### d1_chatbot/
(Reserved for future development)
- Planned chatbot-style interaction improvements

### d2_multi_agent/
Advanced version using multi-agent architecture
- LangGraph implementation
- Multiple specialized agents
- Enhanced state management
- File: `app3.py`

## Versions

### `app2.py`: Enhanced Version with Agent-Based Architecture
The enhanced version implements a sophisticated multi-agent system using LangChain and LangGraph for more intelligent gameplay.

#### Key Features
- **Agent-Based Architecture**
  - Central Interaction Agent: Manages game flow and communication
  - Word Generator Agent: Handles word selection and metadata
  - Game Logic Agent: Processes guesses and game state
  - Hint and Feedback Agent: Provides intelligent hints
  - Scoring Agent: Manages game scoring and statistics

#### Technical Improvements
- LangGraph implementation for structured agent communication
- State management using TypedDict for better type safety
- Directed graph workflow for game logic
- Enhanced error handling and state recovery
- Improved hint generation system

#### Graph Structure
- Nodes: generate_word, process_guess, generate_hint
- Conditional routing based on game state
- Compiled graph for optimized performance

### `app.py`: Initial Version

## Features (app.py)

### Core Functionality
- Dynamic word generation using OpenAI's GPT-3.5 model
- Intelligent hint system that provides context-aware clues
- Maximum 10 attempts per game
- Word diversity system to prevent repetition

### Game Interface
- Clean, modern web interface
- Real-time attempt counter (0/10)
- Chat-style interaction between player and AI

### Game Controls
- Start New Game button
- Restart Game button (reveals current word before starting new game)
- Exit Game button (reveals word before closing)
- Submit Guess functionality

### AI Integration
- OpenAI API for random word generation
- LangChain integration for intelligent hint generation
- Strict hint system that never reveals the answer directly

### Game Rules
1. Player has 10 attempts to guess the word
2. AI provides hints after each guess
3. Game ends when:
   - Player correctly guesses the word
   - Player reaches maximum attempts (10)
   - Player chooses to give up
   - Player exits or restarts the game

## Technical Implementation
- Backend: Python Flask
- AI Integration: OpenAI API, LangChain
- Frontend: HTML, JavaScript
- State Management: Server-side game state
- Environment Variables: Secure API key storage

## Future Development
The next version (`app2.py`) will build upon this foundation to introduce more complex features and gameplay mechanics.

## Setup
1. Create a `.env` file with your OpenAI API key:
