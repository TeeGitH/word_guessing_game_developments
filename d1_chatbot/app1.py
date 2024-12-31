from typing import TypedDict, List
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from pathlib import Path
import graphviz

# Get the root directory (parent of d1_chatbot)
root_dir = Path(__file__).parent.parent

# Load environment variables from root directory
load_dotenv(root_dir / '.env')

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Define our state
class State(TypedDict):
    messages: List[dict]
    attempts: int

def create_chat_graph():
    # Create the graph
    workflow = StateGraph(State)
    
    def chatbot(state: State) -> dict:
        """Process chat messages and return response"""
        # Prepare messages for API call
        messages = [
            {"role": "system", "content": "You are a friendly word guessing game host. Never reveal the word unless the player explicitly says 'I give up'."},
            *state["messages"][-5:]  # Keep last 5 messages
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

    # Add node
    workflow.add_node("chatbot", chatbot)
    workflow.set_entry_point("chatbot")
    
    def router(state: State) -> str:
        if state["attempts"] >= 10:  # Max attempts reached
            return END
            
        last_message = state["messages"][-1]["content"].lower()
        if "quit" in last_message or "exit" in last_message:
            return END
        return "chatbot"

    workflow.add_conditional_edges(
        "chatbot",
        router,
        {
            "chatbot": "chatbot",
            END: END
        }
    )

    return workflow.compile()

def save_workflow_graph():
    """Create and save a visualization of the workflow"""
    dot = graphviz.Digraph(comment='Word Guessing Game Workflow')
    dot.attr(rankdir='TB')  # Top to bottom layout
    
    # Add nodes
    dot.node('START', 'Start', shape='oval')
    dot.node('HUMAN', 'Human Input\n(Guess/Hint Request)', shape='box', style='rounded')
    dot.node('CHATBOT', 'Chatbot\nProcess Message', shape='box')
    dot.node('CHECK', 'Check State', shape='diamond')
    dot.node('END', 'End Game', shape='oval')
    
    # Add edges
    dot.edge('START', 'HUMAN', 'Initial Greeting')
    dot.edge('HUMAN', 'CHATBOT', 'Send Message')
    dot.edge('CHATBOT', 'CHECK', 'Process Complete')
    dot.edge('CHECK', 'HUMAN', 'Continue\n(attempts < 10)')
    dot.edge('CHECK', 'END', 'Exit\n(attempts >= 10 or quit)')
    
    # Save the graph
    dot.render(Path(__file__).parent / 'workflow_graph', format='png', cleanup=True)

if __name__ == "__main__":
    # Generate and save the workflow graph
    try:
        save_workflow_graph()
        print("Workflow graph saved as 'workflow_graph.png'")
    except Exception as e:
        print(f"Error saving workflow graph: {str(e)}")
    
    app = create_chat_graph()
    
    # Initialize state
    state = {
        "messages": [
            {"role": "user", "content": "Hi, let's play a word guessing game!"}
        ],
        "attempts": 0
    }
    
    try:
        # Run the graph
        result = app.invoke(
            state,
            config={
                "configurable": {
                    "thread_id": "chat_1",
                    "checkpoint_ns": "word_game",
                    "checkpoint_id": "session_1"
                }
            }
        )
        print("\nChat flow completed!")
        for message in result["messages"]:
            print(f"{message['role'].upper()}: {message['content']}")
    except Exception as e:
        print(f"Error: {str(e)}")
        # Print API key status (without revealing the key)
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            print("API key not found in environment variables")
        else:
            print(f"API key found (length: {len(api_key)})") 