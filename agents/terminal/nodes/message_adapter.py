import json

from langchain_core.messages import ToolMessage

from agents.terminal.state import TerminalState
from agents.terminal.models import ObservationInput


def message_adapter_node(state: TerminalState):

    messages = state["messages"]

    latest_tool_message = None

    for message in reversed(messages):
        if isinstance(message, ToolMessage):
            latest_tool_message = message
            break

    if latest_tool_message is None:
        raise ValueError("No ToolMessage found.")

    try:
        raw_result = json.loads(latest_tool_message.content)

    except json.JSONDecodeError:
        raw_result = latest_tool_message.content

    observation_input = ObservationInput(
        source="tool",
        tool_name=latest_tool_message.name,
        success=(
            raw_result.get("success", True)
            if isinstance(raw_result, dict)
            else True
        ),
        raw_result=raw_result,
    )

    print("\n[MESSAGE ADAPTER]")
    print(observation_input)

    return {
        "observation_input": observation_input
    }