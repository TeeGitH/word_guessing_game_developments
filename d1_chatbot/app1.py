from typing import Dict, List, Optional, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv
import os
from IPython.display import Image, display

# Load environment variables
load_dotenv()

# Define our state with type hints
class ChatState(TypedDict):
    messages: List[BaseMessage]
    game_active: bool
    current_word: Optional[str]
    attempts: int
    chat_history: List[str]
    hint_level: int
    should_end: bool  # New: explicit end state flag

def create_chat_graph():
    # Initialize LLM with chat prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a friendly word guessing game host. Be engaging and encouraging."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ])
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
    
    # Create the graph
    workflow = StateGraph(ChatState)
    
    # Define the nodes with proper state handling
    def chat_interaction(state: ChatState) -> Dict:
        """Main chatbot interaction node"""
        messages = state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response], "should_end": False}
    
    def process_game_action(state: ChatState) -> Dict:
        """Process game-related actions"""
        # Game logic implementation here
        return {"messages": state["messages"], "should_end": False}
    
    def end_conversation(state: ChatState) -> Dict:
        """Handle game ending"""
        farewell = AIMessage(content="Thanks for playing! Goodbye!")
        return {"messages": [farewell], "should_end": True}
    
    # Add nodes
    workflow.add_node("chat", chat_interaction)
    workflow.add_node("game", process_game_action)
    workflow.add_node("end", end_conversation)
    
    # Define the router
    def router(state: ChatState) -> str:
        if state.get("should_end", False):
            return END
        
        messages = state["messages"]
        if not messages:
            return "chat"
            
        last_message = messages[-1].content.lower()
        
        if "exit" in last_message or "quit" in last_message:
            return "end"
        elif state["game_active"]:
            return "game"
        else:
            return "chat"
    
    # Set up the graph structure
    workflow.set_entry_point("chat")
    
    # Add edges with conditional routing
    workflow.add_conditional_edges(
        "chat",
        router,
        {
            "chat": "chat",
            "game": "game",
            "end": "end",
            END: END
        }
    )
    
    workflow.add_conditional_edges(
        "game",
        router,
        {
            "chat": "chat",
            "end": "end",
            END: END
        }
    )
    
    workflow.add_edge("end", END)
    
    return workflow.compile()

def init_chat_state() -> ChatState:
    return {
        "messages": [
            SystemMessage(content="You are a friendly word guessing game host. Be engaging and encouraging.")
        ],
        "game_active": False,
        "current_word": None,
        "attempts": 0,
        "chat_history": [],
        "hint_level": 0,
        "should_end": False
    }

def visualize_graph(workflow):
    """Save and display the graph visualization"""
    try:
        # Save the graph visualization as PNG
        graph_image = workflow.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("d1_chatbot/chat_flow_graph.png", "wb") as f:
            f.write(graph_image)
            
        print("Graph visualization saved as 'chat_flow_graph.png'")
        
        # Display the graph
        display(Image(graph_image))
    except Exception as e:
        print(f"Failed to visualize graph: {e}")

# Test the graph
if __name__ == "__main__":
    # Create and compile the graph
    workflow = StateGraph(ChatState)
    
    # Add nodes and edges (same as in create_chat_graph)
    # ... [previous node and edge definitions] ...
    
    # Compile the graph
    app = workflow.compile()
    
    # Visualize the graph
    visualize_graph(app)
    
    # Test the flow
    state = init_chat_state()
    state["messages"].append(HumanMessage(content="Hi, let's play a game!"))
    
    try:
        result = app.invoke(state)
        print("\nChat flow completed successfully!")
        for message in result["messages"]:
            print(f"{message.type}: {message.content}")
    except Exception as e:
        print(f"Error in chat flow: {str(e)}") 