from langgraph.graph import END

def critic_router(state):

    if state["critic_decision"] == "EXECUTE":
        return "executor"

    return END