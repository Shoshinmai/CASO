BLOCKED_PATTERNS = [

    "del ",
    "rmdir ",
    "rm ",
    "format ",
    "shutdown ",
    "taskkill ",
    "reg delete ",
]

def safety_filter_node(state):

    command = state["command"].lower()

    for pattern in BLOCKED_PATTERNS:

        if pattern in command:

            return {
                "safe": False,
                "critic_feedback":
                    f"Blocked command: {pattern}"
            }

    return {
        "safe": True
    }