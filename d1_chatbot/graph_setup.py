from langgraph.graph import StateGraph, END, START
from agent_state import GameState
from nodes import chatbot_node

# Define constant for chatbot node
CHATBOT = "chatbot"

def create_game_graph():
    """Create and configure the game workflow graph with a Chatbot node."""
    # Create the graph
    workflow = StateGraph(GameState)
    
    # Add chatbot node
    workflow.add_node(CHATBOT, chatbot_node)
    
    # Add edges - from START to chatbot, and from chatbot to END
    workflow.add_edge(START, CHATBOT)
    workflow.add_edge(CHATBOT, END)
    
    # Add conditional edge for chatbot to continue processing
    def router(state: GameState) -> str:
        return END if not state["game_active"] else CHATBOT
    
    workflow.add_conditional_edges(
        CHATBOT,
        router,
        {
            CHATBOT: CHATBOT,
            END: END
        }
    )
    
    return workflow.compile()

def save_workflow_visualization():
    """
    Create and save a visualization of the workflow using Mermaid.
    This visualization exactly matches the graph structure in create_game_graph:
    1. START -> CHATBOT (initial edge)
    2. CHATBOT -> END (direct edge)
    3. CHATBOT -> CHATBOT (conditional edge when game_active is True)
    """
    # Create and compile the graph
    graph = create_game_graph()
    
    try:
        # Get the Mermaid graph representation
        mermaid_graph = graph.get_graph()
        
        # Save the Mermaid graph as PNG
        png_data = mermaid_graph.draw_mermaid_png()
        
        # Write the PNG data to a file
        with open('workflow_graph.png', 'wb') as f:
            f.write(png_data)
            
        print("Graph visualization saved as workflow_graph.png")
    except Exception as e:
        print(f"Error saving graph visualization: {str(e)}")
        print("Note: Mermaid visualization requires additional dependencies")
