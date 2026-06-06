import json

from llm.prompts import (
    CRITIC_PROMPT
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


def build_critic_prompt():

    return CRITIC_PROMPT.format(
        available_tools=
        build_tool_section()
    )