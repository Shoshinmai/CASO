from tools.registry import register_tool

from tools.implementations.open_app import (
    OpenAppTool
)

from tools.implementations.open_url import (
    OpenUrlTool
)

register_tool(
    OpenAppTool()
)

register_tool(
    OpenUrlTool()
)