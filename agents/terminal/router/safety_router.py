
def safety_router(state):

    if state["safe"]:
        return "critic"

    return "end"