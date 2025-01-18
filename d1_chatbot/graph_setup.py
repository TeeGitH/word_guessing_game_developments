from langgraph.graph import StateGraph, END
from agent_state import GameState
from nodes import process_guess, check_game_status, get_random_word
import graphviz

# Define START constant since it's not provided by langgraph
START = "start"

def create_game_graph():
    """Create and configure the game workflow graph."""
    # Create the graph
    workflow = StateGraph(GameState)
    
    # Define the start node that initializes the game
    def start_node(state: GameState) -> dict:
        """Initialize the game with a random word."""
        return {
            "current_word": get_random_word(),
            "game_active": True,
            "messages": [{"role": "user", "content": "Hi, let's play a word guessing game!"}]
        }
    
    # Add nodes
    workflow.add_node(START, start_node)
    workflow.add_node("process_guess", process_guess)
    
    # Set the entry point to start
    workflow.set_entry_point(START)
    
    # Add edges
    workflow.add_edge(START, "process_guess")
    
    # Add conditional edges based on game status
    def router(state: GameState) -> str:
        status = check_game_status(state)
        return "process_guess" if status == "CONTINUE" else END
    
    workflow.add_conditional_edges(
        "process_guess",
        router,
        {
            "process_guess": "process_guess",
            END: END
        }
    )
    
    return workflow.compile()

def save_workflow_visualization():
    """Create and save a visualization of the workflow."""
    dot = graphviz.Digraph('Word_Guessing_Game_Workflow', comment='Word Guessing Game Workflow')
    
    # Set graph attributes
    dot.attr(rankdir='TB')  # Top to bottom layout
    
    # Add nodes with specific shapes
    dot.node(START, 'Start', shape='oval')
    dot.node('human_input', 'Human Input\n(Guess/Hint Request)', shape='oval')
    dot.node('chatbot', 'Chatbot\nProcess Message', shape='box')
    dot.node('check_state', 'Check State', shape='diamond')  # Diamond shape for decision points
    dot.node('end', 'End Game', shape='oval')
    
    # Add edges with labels
    dot.edge(START, 'human_input', 'Initial Greeting')
    dot.edge('human_input', 'chatbot', 'Send Message')
    dot.edge('chatbot', 'check_state', 'Process Complete')
    dot.edge('check_state', 'human_input', 'Continue\n(attempts < 10)')
    dot.edge('check_state', 'end', 'Exit\n(attempts >= 10 or quit)')
    
    # Save the graph
    dot.render('workflow_graph', format='png', cleanup=True)
