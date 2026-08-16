"""
Runtime Graph integration test.

Validates the normal Runtime lifecycle:

    INITIALIZING
        ↓ TASK_READY
    PLANNING
        ↓ PLAN_CREATED
    EXECUTING
        ↓ EXECUTION_COMPLETED
    REVIEWING

This test intentionally mocks the LLM-backed Planner, Executor,
and Critic nodes.

The purpose of this test is to validate graph/runtime wiring,
NOT the LLM outputs themselves.
"""

from __future__ import annotations

from typing import Any

from agents.terminal.runtime.events import RuntimeEvent
from agents.terminal.runtime.modes import RuntimeMode
from agents.terminal.runtime.models import RuntimeState
from agents.terminal.runtime.stages import RuntimeStage
from agents.terminal.state import TerminalState


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def fake_planner_node(
    state: TerminalState,
) -> dict[str, Any]:
    """
    Simulate a successful Planner.

    We don't call the actual LLM here because this test is validating
    Runtime Graph routing.
    """

    runtime_state = state["runtime_state"]

    print("\n[PLANNER]")
    print("Runtime mode:", runtime_state.mode)

    assert runtime_state.mode == RuntimeMode.PLANNING

    return {
        "planner_output": "fake planner output",
        "task_plan": "fake task plan",
    }


def fake_executor_node(
    state: TerminalState,
) -> dict[str, Any]:
    """
    Simulate a successful Executor.
    """

    runtime_state = state["runtime_state"]

    print("\n[EXECUTOR]")
    print("Runtime mode:", runtime_state.mode)

    assert runtime_state.mode == RuntimeMode.EXECUTING

    return {
        "execution_workflow": "fake execution workflow",
    }


def fake_critic_node(
    state: TerminalState,
) -> dict[str, Any]:
    """
    Simulate a Critic invocation.

    For this test we stop after reaching REVIEWING.
    The Critic's actual decision routing is tested separately.
    """

    runtime_state = state["runtime_state"]

    print("\n[CRITIC]")
    print("Runtime mode:", runtime_state.mode)

    assert runtime_state.mode == RuntimeMode.REVIEWING

    return {
        "critic_output": "fake critic output",
    }


# ------------------------------------------------------------------
# Test 1
# ------------------------------------------------------------------

def test_runtime_graph_happy_path():
    """
    Validate:

        INITIALIZING
            ↓ TASK_READY
        PLANNING
            ↓ PLAN_CREATED
        EXECUTING
            ↓ EXECUTION_COMPLETED
        REVIEWING
    """

    from agents.terminal.runtime.kernel import RuntimeKernel

    runtime_state = RuntimeState()

    print("\n========================================")
    print("RUNTIME GRAPH HAPPY PATH TEST")
    print("========================================")

    # --------------------------------------------------------------
    # Initial state
    # --------------------------------------------------------------

    print("\n[INITIAL]")
    print("Mode:", runtime_state.mode)

    assert runtime_state.mode == RuntimeMode.INITIALIZING

    # --------------------------------------------------------------
    # TASK_READY
    # --------------------------------------------------------------

    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.TASK_READY,
    )

    print("\n[TASK_READY]")
    print("Mode:", runtime_state.mode)
    print("Last event:", runtime_state.last_event)
    print("Stage:", stage)

    assert runtime_state.mode == RuntimeMode.PLANNING
    assert runtime_state.last_event == RuntimeEvent.TASK_READY
    assert stage == RuntimeStage.PLANNER

    # --------------------------------------------------------------
    # Planner
    # --------------------------------------------------------------

    state = {
        "runtime_state": runtime_state,
    }

    fake_planner_node(state)

    # --------------------------------------------------------------
    # PLAN_CREATED
    # --------------------------------------------------------------

    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.PLAN_CREATED,
    )

    print("\n[PLAN_CREATED]")
    print("Mode:", runtime_state.mode)
    print("Last event:", runtime_state.last_event)
    print("Stage:", stage)

    assert runtime_state.mode == RuntimeMode.EXECUTING
    assert runtime_state.last_event == RuntimeEvent.PLAN_CREATED
    assert stage == RuntimeStage.EXECUTOR

    # --------------------------------------------------------------
    # Executor
    # --------------------------------------------------------------

    state = {
        "runtime_state": runtime_state,
    }

    fake_executor_node(state)

    # --------------------------------------------------------------
    # EXECUTION_COMPLETED
    # --------------------------------------------------------------

    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.EXECUTION_COMPLETED,
    )

    print("\n[EXECUTION_COMPLETED]")
    print("Mode:", runtime_state.mode)
    print("Last event:", runtime_state.last_event)
    print("Stage:", stage)

    assert runtime_state.mode == RuntimeMode.REVIEWING
    assert runtime_state.last_event == RuntimeEvent.EXECUTION_COMPLETED
    assert stage == RuntimeStage.CRITIC

    # --------------------------------------------------------------
    # Critic
    # --------------------------------------------------------------

    state = {
        "runtime_state": runtime_state,
    }

    fake_critic_node(state)

    print("\n========================================")
    print("HAPPY PATH PASSED")
    print("========================================")


# ------------------------------------------------------------------
# Test 2
# ------------------------------------------------------------------

def test_runtime_initialization_transition():
    """
    Specifically validates the 7.1.16 fix:

        INITIALIZING + TASK_READY → PLANNING
    """

    from agents.terminal.runtime.kernel import RuntimeKernel

    runtime_state = RuntimeState()

    assert runtime_state.mode == RuntimeMode.INITIALIZING

    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.TASK_READY,
    )

    assert runtime_state.mode == RuntimeMode.PLANNING
    assert runtime_state.last_event == RuntimeEvent.TASK_READY
    assert stage == RuntimeStage.PLANNER

    print("\nInitialization transition passed.")


# ------------------------------------------------------------------
# Test 3
# ------------------------------------------------------------------

def test_runtime_normal_transition_chain():
    """
    Validate the Runtime Kernel transitions without any graph nodes.
    """

    from agents.terminal.runtime.kernel import RuntimeKernel

    runtime_state = RuntimeState()

    # INITIALIZING → PLANNING
    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.TASK_READY,
    )

    assert runtime_state.mode == RuntimeMode.PLANNING
    assert stage == RuntimeStage.PLANNER

    # PLANNING → EXECUTING
    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.PLAN_CREATED,
    )

    assert runtime_state.mode == RuntimeMode.EXECUTING
    assert stage == RuntimeStage.EXECUTOR

    # EXECUTING → REVIEWING
    stage = RuntimeKernel.handle_event(
        runtime_state=runtime_state,
        event=RuntimeEvent.EXECUTION_COMPLETED,
    )

    assert runtime_state.mode == RuntimeMode.REVIEWING
    assert stage == RuntimeStage.CRITIC

    print("\nRuntime transition chain passed.")