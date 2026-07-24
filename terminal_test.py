from agents.terminal.graph import terminal_graph

config = {"configurable": {"thread_id": "caso-3"}}

result = terminal_graph.invoke(
    {
        "goal": "Find all planner-related files in the project and explain how the planner is implemented.",
        # "goal": "Analyze the current directory and look for planner files.",
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
    },
    config=config,
)

print("\n[DONE]")
print(result)
