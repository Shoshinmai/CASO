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
            "Perform a read-only multi-step investigation of the current CASO project "
        "using one continuous execution workflow. "
        
        "Step 1: Locate the file named runtime_graph_execution_test.py and return "
        "its exact absolute path. "
        
        "Step 2: Using the exact path discovered in Step 1, read the file and "
        "identify the Python module imported on the first non-comment import line. "
        
        "Step 3: Using the exact module name discovered in Step 2, determine the "
        "corresponding Python source filename and locate that exact file in the "
        "current CASO project. "
        
        "Step 4: Using the exact source path discovered in Step 3, read the source "
        "file and identify the function or symbol used to define the main graph "
        "entry point. "
        
        "Step 5: Using all information discovered by the previous steps, produce "
        "a final report containing the exact test file path, imported module, "
        "runtime graph source path, and main graph entry point. "
        
        "The important requirement is that each step must use information produced "
        "by the immediately preceding step rather than independently rediscovering "
        "the information. Do not hard-code any paths or filenames. "
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


# test_terminal_agent_replanning()

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


test_terminal_agent_final_termination_cleanup()