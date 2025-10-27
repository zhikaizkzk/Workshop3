from typing import Literal
from state import State


def human_node(state: State) -> dict:
    """
    Human input node - gets user input and sets volley count.
    """
    user_input = input("\nYou: ").strip()
    
    human_message = {
        "role": "user",
        "content": f"You: {user_input}"
    }

    messages = state.get("messages", []).copy()
    messages.append(human_message)
    return {
        "messages": messages
    }


def check_exit_condition(state: State) -> Literal["summarizer", "coordinator"]:
    """
    Check if user typed 'exit' to end conversation.
    """
    messages = state.get("messages", [])

    if messages:
        last_message = messages[-1]
        content = last_message.get("content", "").lower()
        if "exit" in content:
            return "END"
        
    return "coordinator"


def coordinator_routing(state: State) -> Literal["participant", "human"]:
    """
    Route from coordinator based on volley count.
    """
    volley_left = state.get("volley_msg_left", 0)

    if volley_left > 0:
        return "participant"
    
    return "human"
