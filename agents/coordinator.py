from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from state import State
from utils import debug

def coordinator(state: State) -> dict:
    """
    Select next speaker based on conversation context.
    Manages volley control and updates state accordingly.

    Updates state with:
    - next_speaker: Selected agent ID or "human"
    - volley_msg_left: Decremented counter

    Returns: Updated state
    """

    debug(state)
    volley_left = state.get("volley_msg_left", 0)
    debug(f"Volley messages left: {volley_left}", "COORDINATOR")

    if volley_left < 0:
        debug("No volleys left, returning to human", "COORDINATOR")
        return {
            "next_speaker": "human",
            "volley_msg_left": -1
        }

    messages = state.get("messages", [])

    conversation_text = ""
    for msg in messages:
        # Messages are now always dicts
        conversation_text += f"{msg.get('content', '')}\n"


    system_prompt = """You are managing a lively conversation at a group discussion for next travel plan.

    Available speakers:
    - Ken: An adventurous traveller who loves exploring new countries and cultures
    - Melody: A shopping freak who likes to buy souvenirs and trendy items from her travels
    - Gary: A book nerd who enjoys reading about history and culture of the places he visits

    Based on the conversation flow, select who should speak next to keep the conversation lively and natural.
    Consider:
    - Who hasn't spoken recently
    - The next speaker should not be the same person as the current speaker
    - Try to involve every one, and make the the discussion is evenly distributed


    Respond with ONLY the speaker ID (ken, melody, or gary).
    """

    user_prompt = f"""Recent conversation:
    {conversation_text}

    Who should speak next to keep this group discussion conversation lively?"""

    # Call LLM
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=1)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        # Extract speaker from response
        if isinstance(response.content, list):
            selected_speaker = " ".join(str(item) for item in response.content).strip().lower()
        else:
            selected_speaker = str(response.content).strip().lower()
        debug(f"LLM selected: {selected_speaker}", "COORDINATOR")

        # Validate speaker
        valid_speakers = ["ken", "melody", "gary"]
        if selected_speaker not in valid_speakers:
            # Fallback to round-robin if invalid
            import random
            selected_speaker = random.choice(valid_speakers)
            debug(f"Invalid speaker, fallback to: {selected_speaker}", "COORDINATOR")

    except Exception as e:
        # Fallback selection if LLM fails
        import random
        valid_speakers = ["ken", "melody", "gary"]
        selected_speaker = random.choice(valid_speakers)
        debug(f"LLM error, random selection: {selected_speaker}", "COORDINATOR")

    debug(f"Final selection: {selected_speaker} (volley {volley_left} -> {volley_left - 1})", "COORDINATOR")

    # Return only the updates (LangGraph will merge with existing state)
    return {
        "next_speaker": selected_speaker,
        "volley_msg_left": volley_left - 1
    }
