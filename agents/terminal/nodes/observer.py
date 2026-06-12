def terminal_observer_node(state):

    print("\n[TERMINAL OUTPUT]")
    print(state["output"])

    if state["error"]:
        print("\n[TERMINAL ERROR]")
        print(state["error"])

    return {}