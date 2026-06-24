from agents.terminal.graph import terminal_graph

result = terminal_graph.invoke(
    {
        "goal": "Find all python files in this project and locate main.py",
        "thought": "",
        "command": "",
        "raw_observation": "",
        "compressed_observation": "",
        "artifact_id": "",
        "success": False,
        "error": "",
        "done": False,
        "step_count": 0,
        "scratchpad": "",
        "valid_command": True,
        "validation_error": "",
        "safety_passed": True,
        "safety_reason": "",
    }
)

print("\n[DONE]")
print(result)
