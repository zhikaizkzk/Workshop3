from langchain_openai import ChatOpenAI
## older package
#from langchain.schema import HumanMessage, SystemMessage

## newer packages
from langchain_core.messages import HumanMessage, SystemMessage
from tools import flights_timing
import re

from utils import debug


def execute_tool(tool_name):
    """
    Execute a specific tool and return its output.
    Returns Tool output as string
    """
    tool_name = tool_name.lower().strip()

    if tool_name == "flight":
        return flights_timing()
    else:
        return f"Unknown tool: {tool_name}"


def flight_agent(state) -> str:
    """
    Generate summary report using LLM when conversation ends.

    Args:
        state: Current conversation state with messages

    Returns:
        Formatted summary string
    """
    messages = state.get("messages", [])

    if not messages:
        return "No conversation to summarize."

    # Extract conversation text
    conversation_text = ""
    for msg in messages:
        # Messages are now always dicts
        conversation_text += f"{msg.get('content', '')}\n"

    if not conversation_text.strip():
        return "No conversation content to summarize."
    # Tool descriptions mapping
    tool_descriptions = {
        "flight": "Returns an amount of data",
    }

    # Build available actions list based on persona's tools
    available_actions = ""
    available_actions += f"\n\n{"flight"}:\n{tool_descriptions["flight"]}"
    # System prompt for summarization
    system_prompt = f"""You are a flight planner agent who has been listening to the group discussion about the next travel plan.

Generate a good flight timing based on:
1. the traveller group discussion agreements and disagreement
2. The dynamics between participants
3. The overall mood and flow of the conversation
4. Always start from Singapore to travel to a destination


Use Thought to describe your thoughts about the group discussion and your planning.
Use Action to run one of the actions available to you.
Observation will be the result of running those actions.


Possible actions are:

{available_actions}

You only have access to the tools/actions listed above. Do not call tools that you do not have access to.

Example session:

Thought: I want to travel to Thailand
Action: flight

You will be called again with:
Observation: [Actual flights returned after you call the tool, with pagination and data. use the data available to set up a plan]

You must never try to guess the flights. Rely on the Observation that you will be called later on for the answers. if there are not matching dates, based on the data. Get the latest flight
based on the Observation of the dataset.

Once you have gathered the data, DO NOT CALL THE TOOL AGAIN.

ONLY ADD IN MESSAGE WHEN YOU HAVE YOUR DATA AND ANSWER:
Message: [Your response as a AI having a summary for the group discussion]

Format your flight timing  in a clear way that captures time, arrival and destination of the flight.
Keep it concise but insightful."""

    user_prompt = f"""Here's the conversation that took place:

{conversation_text}


IMPORTANT:
- You must not be providing Observation in your response. Observation is a result from tool, not for you to respond.
- Once you have enough information, output Message: followed by your response
- YOU MUST COME TO A CONCLUSION WITHIN 3 LOOPS BASED ON THE DATA YOU HAVE RETRIEVED

Please provide a flight plan of this group discussion."""

    max_iterations = 3  # Prevent infinite loops
    for iteration in range(max_iterations):
        print(iteration)
        print("this is my iteration")
        print(user_prompt)
        try:
            # Call LLM
            llm = ChatOpenAI(model="gpt-5-nano", temperature=1)

            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            content = response.content.strip()
            print("answered but dk the message")
            print(response.content)
            # Check if the response contains Action:
            if "Action:" in content:
                # Extract the action
                action_match = re.search(r'Action:\s*(\w+)', content)
                if action_match:
                    tool_name = action_match.group(1)
                    debug(f"Executing tool: {tool_name}")

                    # Execute the tool
                    observation = execute_tool(tool_name)
                    debug(f"Observation: {observation}")
                    debug("")  # Empty line for readability
                    user_prompt += f"\n\n\nObservation: {observation}\n"
                    print("i am finished answering")
                    print(response.content)
                    continue  # loop again with the new data
            # If model reaches a Message (final answer)
            if "Message:" in content:
                message_text = re.sub(r"^.*Message:\s*", "", content, flags=re.S)
                print("yup here")
                return {"internalsummary": f"=== FLIGHT PLAN SUMMARY ===\n\n{message_text.strip()}"}
            # if isinstance(response.content, list):
            #     summary = " ".join(str(item) for item in response.content).strip()
            # else:
            #     summary = str(response.content).strip()

            # Format with header


        except Exception as e:
            # Fallback to basic summary if LLM fails
            return f"""=== FLIGHT PLAN SUMMARY ===
            
            Total messages: {len(messages)}
            
            Unable to generate detailed summary at this time.
            The conversation has been logged for review."""

        return {"internalsummary": "=== FLIGHT PLAN SUMMARY ===\n\nNo final message received after 3 iterations."}