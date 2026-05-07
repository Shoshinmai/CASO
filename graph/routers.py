def route_after_critic(state):
    decision = state["critic_decision"]

    if decision == "REVISE":
        return "planner"

    if decision == "RETRY":
        return "ambiguity"

    return "executor"

def route_after_validator(state):
    return "invalid" if state["validation_error"] else "critic"