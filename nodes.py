from typing import Literal
from agents import traveller
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
        "messages": messages,
        "volley_msg_left": 5  # Set volley count
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


def coordinator_routing(state: State) -> Literal["traveller", "human"]:
    """
    Route from coordinator based on volley count.
    """
    volley_left = state.get("volley_msg_left", -1)

    if volley_left >= 0:
        return "traveller"
    
    return "human"

def traveller_node(state: State) -> dict:
    """
    Traveller node - calls the appropriate traveller and handles output.
    """
    next_speaker = state.get("next_speaker", "ken")  # Default fallback

    # Call participant with the selected speaker
    result = traveller(next_speaker, state)

    # Print and return messages
    if result and "messages" in result:
        messages = state.get("messages", []).copy()
        for msg in result["messages"]:
            print(msg.get("content", ""))
            messages.append(msg)

        return {"messages": messages}

    return {}