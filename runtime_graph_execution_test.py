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


def test_terminal_agent_retry_path():

    initial_state = {
        "goal": (
            """
            Run a terminal command that uses a marker file named
terminal_retry_once_marker.txt.

On the first execution:
- if the marker does not exist, create it and exit with a non-zero
  return code.

On a subsequent execution:
- if the marker exists, print "RETRY_SUCCESS", delete the marker,
  and exit with code 0.

The task should be considered complete only after the command succeeds.
"""
        ),
    }

    result = runtime_graph.invoke(
        initial_state,
        config,
    )

    assert result is not None

    print("\n")
    print("=" * 60)
    print("7.2.x.2 — RETRY PATH TEST")
    print("=" * 60)

    print("\n[FINAL STATE]")
    print(result)


test_terminal_agent_retry_path()


def test_terminal_agent_final_termination_cleanup():

    initial_state = {
        "goal": "Show the Python version currently available on this system.",
    }

    result = runtime_graph.invoke(
        initial_state,
        config,
    )

    assert result is not None

    print("\n")
    print("=" * 60)
    print("TERMINAL AGENT FINAL TERMINATION / CLEANUP TEST")
    print("=" * 60)

    print("\n[FINAL STATE]")
    print(result)

    runtime_state = result.get("runtime_state")
    execution_workflow = result.get("execution_workflow")
    ephemeral_state = result.get("ephemeral_execution_state")

    print("\n[TERMINATION INVARIANTS]")
    print(f"runtime_state.mode       = {runtime_state.mode}")
    print(f"runtime_state.last_event = {runtime_state.last_event}")
    print(f"execution_workflow       = {execution_workflow}")
    print(f"current_attempt_id       = {ephemeral_state.current_attempt_id}")

    assert runtime_state.mode.value == "finished"
    assert runtime_state.last_event.value == "goal_completed"

    assert execution_workflow is None

    assert ephemeral_state.current_attempt_id is None

    print("\n[RESULT]")
    print("ALL TERMINATION/CLEANUP INVARIANTS PASSED")


# test_terminal_agent_final_termination_cleanup()
