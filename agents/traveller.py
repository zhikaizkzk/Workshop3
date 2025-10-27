from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils import debug
import re


# Persona configurations
PERSONAS = {
    "ken": {
        "name": "Kennedy Khan",
        "age": 34,
        "backstory": "An adventurous traveller who loves exploring new countries and cultures.",
        "personality": "Friendly, curious, enthusiastic about travel",
        "speech_style": "Casual English with sometimes English slang, uses travel jargon"
        # "tools": ["time", "weather"]
    },
    "melody": {
        "name": "Melody Chen",
        "age": 25,
        "backstory": "A shopping freak who likes to buy souvenirs and trendy items from her travels.",
        "personality": "Energetic, talkative, loves fashion and trends",
        "speech_style": "Valley girl style English, lots of slang and trendy phrases"
        # "tools": ["time", "news"]
    },
    "gary": {
        "name": "Gary Tan",
        "age": 28,
        "backstory": "A book nerd who enjoys reading about history and culture of the places he visits.",
        "personality": "Intellectual, thoughtful, a bit introverted",
        "speech_style": "Formal English, well-structured sentences, uses historical references"
        # "tools": ["time"]
    }
}


# def execute_tool(tool_name):
#     """
#     Execute a specific tool and return its output.
#     Returns Tool output as string
#     """
#     tool_name = tool_name.lower().strip()

#     if tool_name == "time":
#         return singapore_time()
#     elif tool_name == "weather":
#         return singapore_weather()
#     elif tool_name == "news":
#         return singapore_news()
#     else:
#         return f"Unknown tool: {tool_name}"


def traveller(persona_id, state) -> dict:
    """
    Generate speech for a persona using ReAct workflow with real tool calling.

    Args:
        persona_id: One of "ken", "melody", "gary"
        state: Current conversation state

    Returns:
        Dict with message updates for state
    """
    if persona_id not in PERSONAS:
        return {"messages": [{"role": "assistant", "content": f"Unknown persona: {persona_id}"}]}

    persona = PERSONAS[persona_id]
    debug(f"\n=== {persona['name']} is thinking... ===")

    # Get recent conversation for context
    messages = state.get("messages", [])
    volley_msg_left = state.get("volley_msg_left", 0)
    conversation_text = ""
    for msg in messages: 
        conversation_text += f"{msg.get('content', '')}\n"

    # System prompt for ReAct
    system_prompt = f"""You are {persona['name']}, {persona['age']} years old.
Background: {persona['backstory']}
Personality: {persona['personality']}
Speech style: {persona['speech_style']}

You are at a group discussion about the next travel plan.

You run in a loop of Thought, Action, Observation.
At the end of the loop you output a Message.

Use Thought to describe your thoughts about the conversation.

Observation will be the result of your thoughts based on the assigned behaviours.

------

Example session:

Thought: I should think of what places to suggest based on the user's input.
Message: [Your response in character]

IMPORTANT:
- Once you have enough information, output Message: followed by your response
- Keep your Message concise (3-4 sentences) and in character
- Try to summarise and make a decision when volley message left is closed to 0
"""

    # Internal loop for ReAct
    max_iterations = 5  # Prevent infinite loops
    internal_context = f"Recent conversation:\n{conversation_text}\n\nContinue the conversation as {persona['name']} with the volley message left: {volley_msg_left}.\n"

    for iteration in range(max_iterations):
        user_prompt = internal_context
        debug(f"Iteration {iteration + 1}/{max_iterations}")

        try:
            llm = ChatOpenAI(model="gpt-5-mini", temperature=1)
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            content = response.content.strip()
            debug(f"LLM Response:\n{content}\n")

            # Check if the response contains Message:
            if "Message:" in content:
                # Extract the message
                message_match = re.search(r'Message:\s*(.*)', content, re.DOTALL)
                if message_match:
                    final_message = message_match.group(1).strip()
                    debug(f"Final Message: {final_message}")
                    debug(f"=== End of {persona['name']}'s thought process ===\n")

                    # Return the message to state
                    return {
                        "messages": [{
                            "role": "assistant",
                            "name": persona['name'],
                            "content": f"\n{persona['name']}: {final_message}\n\n"
                        }]
                    }

            # Check if the response contains Action:
            # if "Action:" in content:
            #     # Extract the action
            #     action_match = re.search(r'Action:\s*(\w+)', content)
            #     if action_match:
            #         tool_name = action_match.group(1)
            #         debug(f"Executing tool: {tool_name}")

            #         # Execute the tool
            #         observation = execute_tool(tool_name)
            #         debug(f"Observation: {observation}")
            #         debug("")  # Empty line for readability

            #         # Add observation to internal context
            #         internal_context += f"\n{content}\n\nObservation: {observation}\n"
            #         continue

            # If we get here without action or message, add to context and continue
            internal_context += f"\n{content}\n"

        except Exception as e:
            # Fallback response if LLM fails
            return {
                "messages": [{
                    "role": "assistant",
                    "name": persona['name'],
                    "content": f"{persona['name']}: Too much information, cannot think now..."
                }]
            }

    # If we exhausted iterations without getting a Message, provide default
    return {
        "messages": [{
            "role": "assistant",
            "name": persona['name'],
            "content": f"{persona['name']}: Well, that's interesting..."
        }]
    }
