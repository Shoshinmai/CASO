from agents.terminal.graph import terminal_graph

result = terminal_graph.invoke(
    {
        # "goal": "locate video files in e drive and count them.",
        "goal": "Analyze the current directory and its subdirectories, then show the files related to the terminal agent.",
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
