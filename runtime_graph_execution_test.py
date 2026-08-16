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
            "Investigate and validate the current CASO Terminal Agent runtime. "
            "First locate the runtime_graph_test.py file in the current "
            "project. Then inspect the test to identify the runtime graph it invokes "
            "and the specific Terminal Agent test function being executed. "
            "Next inspect the runtime graph implementation and identify the graph "
            "entry point and the major execution stages involved in running the "
            "Terminal Agent. "
            "After understanding the execution path, run the identified test. "
            "If execution succeeds, verify from the output that the graph reached "
            "its terminal state and report the execution stages observed. "
            "If execution fails, use the error output to locate and inspect the "
            "relevant source code and explain the failure. "
            "Do not modify, delete, or create project files. "
            "Finally provide a concise investigation report containing the test "
            "file, runtime graph entry point, execution result, stages observed, "
            "and any diagnosed issue."
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
