# Word Guessing Game Development

This repository contains different implementations of a word guessing game, each with increasing complexity and features.

## Project Structure

### d0_simple_langchain/
- Basic implementation using LangChain
- Simple word guessing functionality
- OpenAI integration for word generation

### d1_chatbot/
- Enhanced version with graph-based workflow
- Human-in-the-loop interaction pattern
- Features:
  - Interactive chat-based interface
  - Attempt tracking (max 10 attempts)
  - Memory management for conversation history
  - Workflow visualization

#### Workflow Graph
The game flow in `d1_chatbot/app1.py` follows this pattern:
1. Start → Human Input: Game begins with player's greeting
2. Human Input → Chatbot: Player makes a guess or requests a hint
3. Chatbot → Check State: Process the input and generate response
4. Check State → Human Input: Continue if attempts < 10
5. Check State → End: Exit if max attempts reached or player quits

A visual representation of this workflow is saved as `workflow_graph.png` in the d1_chatbot directory.

### d2_multi_agent/
- Advanced implementation with multiple specialized agents
- Complex interaction patterns
- Enhanced game features

## Setup and Installation

1. Clone the repository
2. Create a `.env` file in the root directory with your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```
3. Install required packages:
   ```bash
   pip install openai python-dotenv langchain langgraph graphviz
   ```

## Running the Game

### Simple Version (d0_simple_langchain)
```bash
python d0_simple_langchain/app.py
```

### Chatbot Version (d1_chatbot)
```bash
python d1_chatbot/app1.py
```

### Multi-Agent Version (d2_multi_agent)
```bash
python d2_multi_agent/app2.py
```

## Features by Version

### d1_chatbot (Current Focus)
- Graph-based workflow management
- Interactive chat interface
- Attempt tracking and limits
- Conversation memory
- Workflow visualization
- Human-in-the-loop interaction pattern

## Dependencies
- OpenAI
- LangChain
- LangGraph
- Graphviz (for workflow visualization)
- python-dotenv (for environment management)

## Note
Make sure to have your OpenAI API key properly configured in the `.env` file before running any version of the game.
