from agents.terminal.graph import (
    terminal_graph
)

result = terminal_graph.invoke(
    {
        "goal": "delete all files",
        "command": "",
        "output": "",
        "error": "",
        "success": False,
        "retry_count": 0
    }
)

print("\n[DONE]")
print(result)