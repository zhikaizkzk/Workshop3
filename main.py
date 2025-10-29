from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from agents import flight_agent
from agents.coordinator import coordinator
from nodes import traveller_node
from state import State
from nodes import (
    human_node,
    check_exit_condition,
    coordinator_routing
)

load_dotenv(override=True)  # Override, so it would use your local .env file

def build_graph():
    """
    Build the LangGraph workfthlow.
    """

    builder = StateGraph(State)

    builder.add_node("human", human_node)
    builder.add_node("coordinator", coordinator)
    builder.add_node("traveller", traveller_node)
    builder.add_node("flight_agent", flight_agent)

    builder.add_edge(START, "human")
    builder.add_conditional_edges("human", check_exit_condition, {
        "flight_agent": "flight_agent",
        "coordinator": "coordinator"
        })
    
    builder.add_conditional_edges("coordinator", coordinator_routing, {
        "traveller": "traveller",
        "human": "human"
        })
    
    builder.add_edge("traveller", "coordinator")

    builder.add_edge("flight_agent", END)


    return builder.compile()


def main():
    print("Chat initiated.")
    print("=== UPCOMING TRIP DISCUSSION ===")
    print("Chat with our amazing explorers! Type 'exit' to end.\n")
    print("Setting: A casual dinner in a typical evening...")
    print("Three travel enthusiasts are discussing their next trip plan.")
    print("Ken is very excited about exploring new places,")
    print("Melody is busy scrolling her phone for new items to collect all over the world,")
    print("and Gary is reading up a catalogue on historical sites to visit.\n")

    graph = build_graph()

    print(graph.get_graph().draw_ascii())

    initial_state = State(
        messages=[],
        volley_msg_left=0,
        next_speaker=None
    )

    try:
        graph.invoke(initial_state)
    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ending conversation...")


if __name__ == "__main__":
    main()
