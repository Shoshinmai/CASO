import json

from llm.prompts import (
    BASE_SYSTEM_PROMPT
)

from tools.registry import (
    list_tools
)


def build_tool_section():

    blocks = []

    for tool in list_tools().values():

        block = f"""
Tool:
{tool.name}

Description:
{tool.description}

Parameters:
{json.dumps(tool.parameters, indent=2)}

Examples:
{json.dumps(tool.examples, indent=2)}
"""

        blocks.append(
            block
        )

    return "\n".join(blocks)


def build_planner_prompt(
    system_state
):

    return BASE_SYSTEM_PROMPT.format(
        active_window=
        system_state.get(
            "active_window",
            "Unknown"
        ),

        running_apps=
        system_state.get(
            "running_apps",
            []
        ),

        available_tools=
        build_tool_section()
    )