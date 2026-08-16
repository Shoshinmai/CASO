from agents.terminal.runtime_graph import runtime_graph

config = {"configurable": {"thread_id": "caso-4"}}

# def test_terminal_agent_full_graph_execution():


#     initial_state = {
#         "goal": "show the Python version",
#     }

#     result = runtime_graph.invoke(
#         initial_state,
#         config,
#     )

#     assert result is not None

#     print("\n")
#     print("=" * 60)
#     print("TERMINAL AGENT FULL GRAPH EXECUTION")
#     print("=" * 60)

#     print("\n[FINAL STATE]")
#     print(result)

# # test_terminal_agent_full_graph_execution()

# def test_terminal_agent_failed_command():

#     initial_state = {
#         "goal": (
#             "Run a command that does not exist and "
#             "report what happened."
#         ),
#     }

#     result = runtime_graph.invoke(
#         initial_state,
#         config,
#     )

#     assert result is not None

#     print("\n")
#     print("=" * 60)
#     print("TERMINAL AGENT FAILED COMMAND TEST")
#     print("=" * 60)

#     print("\n[FINAL STATE]")
#     print(result)

# test_terminal_agent_failed_command()


def test_terminal_agent_replanning():

    initial_state = {
        "goal": (
            "Perform a read-only investigation of the current CASO project. "
            "First locate the file named runtime_graph_execution_test.py. "
            "Then, using the exact file path discovered in the previous step, "
            "read that file and identify the runtime graph module it imports. "
            "Next, using the exact runtime graph module path discovered from "
            "the file contents, locate and inspect that source file. "
            "Finally, use the information discovered in the previous steps "
            "to report the test file path, the imported runtime graph module, "
            "the runtime graph source path, and the main graph entry point. "
            "Do not modify, create, or delete any files."
        ),
    }

    result = runtime_graph.invoke(
        initial_state,
        config,
    )

    assert result is not None

    print("\n")
    print("=" * 60)
    print("TERMINAL AGENT REPLANNING TEST")
    print("=" * 60)

    print("\n[FINAL STATE]")
    print(result)


test_terminal_agent_replanning()
