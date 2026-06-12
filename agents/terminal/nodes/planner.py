from llm.llmclient import call_groq

from agents.terminal.prompts.planner_prompt import (
    TERMINAL_SYSTEM_PROMPT
)
import platform

# system_info = {
#     "os": platform.system()
# }


def terminal_planner_node(state):
    
    prompt = TERMINAL_SYSTEM_PROMPT + f"""

GOAL:
{state["goal"]}

OUTPUT:
"""

    command = call_groq(prompt).strip()

    return {
        "command": command
    }