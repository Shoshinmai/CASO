def route_after_critic(state):
    decision = state["critic_decision"]

    if decision == "REVISE":
        return "planner"

    if decision == "RETRY":
        return "ambiguity"

    return "tool_router"

def route_after_validator(state):
    return "invalid" if state["validation_error"] else "critic"