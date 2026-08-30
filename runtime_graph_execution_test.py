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


import asyncio

from agents.terminal.runtime_graph import runtime_graph


config = {
    "configurable": {
        "thread_id": "caso-4",
    }
}


async def test_terminal_agent_retry_path():

    initial_state = {
        "goal": "Inspect this project's agents/terminal part and tell me how can i improve the critic's concurrency flow as i have not yet defined the critics flow for the concurrent tasks. give me a report on this improvement solution in markdown format. ",
    }

    result = await runtime_graph.ainvoke(
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


# if __name__ == "__main__":
#     asyncio.run(
#         test_terminal_agent_retry_path()
#     )

# def test_terminal_agent_final_termination_cleanup():

#     initial_state = {
#         "goal": "Show the Python version currently available on this system.",
#     }

#     result = runtime_graph.invoke(
#         initial_state,
#         config,
#     )

#     assert result is not None

#     print("\n")
#     print("=" * 60)
#     print("TERMINAL AGENT FINAL TERMINATION / CLEANUP TEST")
#     print("=" * 60)

#     print("\n[FINAL STATE]")
#     print(result)

#     runtime_state = result.get("runtime_state")
#     execution_workflow = result.get("execution_workflow")
#     ephemeral_state = result.get("ephemeral_execution_state")

#     print("\n[TERMINATION INVARIANTS]")
#     print(f"runtime_state.mode       = {runtime_state.mode}")
#     print(f"runtime_state.last_event = {runtime_state.last_event}")
#     print(f"execution_workflow       = {execution_workflow}")
#     print(f"current_attempt_id       = {ephemeral_state.current_attempt_id}")

#     assert runtime_state.mode.value == "finished"
#     assert runtime_state.last_event.value == "goal_completed"

#     assert execution_workflow is None

#     assert ephemeral_state.current_attempt_id is None

#     print("\n[RESULT]")
#     print("ALL TERMINATION/CLEANUP INVARIANTS PASSED")


# test_terminal_agent_final_termination_cleanup()

import asyncio

from agents.terminal.runtime_graph import runtime_graph


async def test_d6_3_concurrent_critic_integration():

    config = {
        "configurable": {
            "thread_id": "d6-3-concurrent-critic",
        }
    }

    initial_state = {
        "goal": (
            "Inspect this project's agents/terminal implementation "
            "and determine whether the current concurrent execution "
            "and Critic flow correctly handles independent tasks."
        ),
    }

    print("\n")
    print("=" * 70)
    print("D.6.3 — CONCURRENT CRITIC INTEGRATION TEST")
    print("=" * 70)

    print("\n[STARTING FULL RUNTIME GRAPH]")

    result = await runtime_graph.ainvoke(
        initial_state,
        config,
    )

    assert result is not None

    # ==========================================================
    # FINAL RUNTIME STATE
    # ==========================================================

    runtime_state = result.get(
        "runtime_state",
    )

    task_plan = result.get(
        "task_plan",
    )

    plan_execution_outcome = result.get(
        "plan_execution_outcome",
    )

    critic_output = result.get(
        "critic_output",
    )

    critic_runtime_event = result.get(
        "critic_runtime_event",
    )

    # ==========================================================
    # PRINT RESULTS
    # ==========================================================

    print("\n========== FINAL RUNTIME STATE ==========")

    print(
        "mode       :",
        runtime_state.mode
        if runtime_state
        else None,
    )

    print(
        "last_event :",
        runtime_state.last_event
        if runtime_state
        else None,
    )

    print(
        "iteration  :",
        runtime_state.iteration
        if runtime_state
        else None,
    )

    print("\n========== TASK PLAN ==========")

    if task_plan is not None:

        print(
            "plan_id:",
            task_plan.plan_id,
        )

        print(
            "status:",
            task_plan.status,
        )

        for task in task_plan.tasks:

            print(
                f"{task.task_id} | "
                f"{task.status.value} | "
                f"deps={task.dependencies}"
            )

    else:

        print("No TaskPlan returned.")

    print("\n========== PLAN EXECUTION OUTCOME ==========")

    print(
        plan_execution_outcome,
    )

    print("\n========== CRITIC OUTPUT ==========")

    print(
        critic_output,
    )

    print("\n========== CRITIC RUNTIME EVENT ==========")

    print(
        critic_runtime_event,
    )

    # ==========================================================
    # INTEGRATION ASSERTIONS
    # ==========================================================

    assert runtime_state is not None

    assert task_plan is not None

    # The graph must not finish in an invalid execution state.
    assert runtime_state.mode.value in {
        "finished",
        "planning",
        "executing",
        "reviewing",
    }

    # The Critic must have been reached.
    assert critic_output is not None

    # The Critic must have produced the runtime-facing decision.
    assert critic_runtime_event is not None

    # The new D.4 fields must survive the Critic boundary.
    assert critic_runtime_event.context is not None

    assert (
        critic_runtime_event.context.decision_scope
        in {
            "task",
            "plan",
            "goal",
        }
    )

    print("\n")
    print("=" * 70)
    print("D.6.3 INTEGRATION TEST PASSED")
    print("=" * 70)

    print(
        "\nThe full runtime successfully traversed:"
    )

    print(
        "concurrent execution"
        " -> execution_completed"
        " -> reviewing"
        " -> critic"
        " -> target-aware decision"
    )


if __name__ == "__main__":
    asyncio.run(
        test_d6_3_concurrent_critic_integration()
    )