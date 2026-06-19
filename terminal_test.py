from agents.terminal.graph import (
    terminal_graph
)

result = terminal_graph.invoke(
    {
        "goal": "find the 'The Finals' games files in e drive only.",

        "thought": "",
        "command": "",
        "observation": "",

        "success": False,
        "error": "",

        "done": False,
        "step_count": 0,

        "scratchpad": "",
        
        "valid_command": True,
        "validation_error": "",

        "safety_passed": True,
        "safety_reason": "",
        
        "raw_observation": "",
        "compressed_observation": ""
    }
)

print("\n[DONE]")
print(result)