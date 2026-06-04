from tools.registry import get_tool


def execute_tool(
    tool_name: str,
    params: dict,
    system_state: dict
):

    tool = get_tool(tool_name)

    if tool is None:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )

    return tool.execute(
        params=params,
        system_state=system_state
    )