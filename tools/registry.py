TOOL_REGISTRY = {}


def register_tool(tool):

    TOOL_REGISTRY[tool.name] = tool


def get_tool(tool_name):

    return TOOL_REGISTRY.get(tool_name)


def list_tools():

    return TOOL_REGISTRY