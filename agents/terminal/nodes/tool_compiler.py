from __future__ import annotations

from typing import Any
from uuid import uuid4

from langchain_core.messages import AIMessage
from langchain_core.tools import BaseTool

from agents.terminal.task_executor.models import ExecutionStep
from agents.terminal.tools import TOOLS


def compile_execution_step(
    step: ExecutionStep,
    tools: list[BaseTool] | None = None,
) -> AIMessage:
    """
    Compile one ExecutionStep into a native LangChain tool call.

    This function is deterministic.

    It does not:
    - select a capability
    - modify the execution strategy
    - call an LLM
    - execute the capability
    - retry failures

    It only validates the selected capability and its arguments,
    then constructs the AIMessage expected by ToolNode.
    """

    available_tools = tools if tools is not None else TOOLS

    tool_map = {
        tool.name: tool
        for tool in available_tools
    }

    tool = tool_map.get(step.capability)

    if tool is None:
        raise ValueError(
            f"Unknown capability '{step.capability}'. "
            f"Available capabilities: "
            f"{', '.join(sorted(tool_map))}"
        )

    arguments = _validate_arguments(
        tool=tool,
        arguments=step.arguments,
    )

    return AIMessage(
        content="",
        tool_calls=[
            {
                "name": tool.name,
                "args": arguments,
                "id": f"call_{uuid4().hex}",
                "type": "tool_call",
            }
        ],
    )


def _validate_arguments(
    *,
    tool: BaseTool,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Validate and normalize arguments against the capability schema.
    """

    if tool.args_schema is None:
        return arguments

    try:
        validated = tool.args_schema.model_validate(
            arguments
        )
    except Exception as exc:
        raise ValueError(
            f"Invalid arguments for capability "
            f"'{tool.name}': {exc}"
        ) from exc

    return validated.model_dump(
        exclude_none=True
    )