from tools.registry import register_tool

from tools.implementations.open_app import (
    OpenAppTool
)

register_tool(
    OpenAppTool()
)