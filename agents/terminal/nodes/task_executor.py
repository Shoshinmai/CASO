from agents.terminal.task_executor.models import ExecutorOutput
from agents.terminal.task_executor.context_builder import (
    build_execution_context,
)
from agents.terminal.prompts.executor_prompt import TERMINAL_EXECUTOR_PROMPT
from llm.llmclient import call_nvidia, call_ollama


def terminal_task_executor_node(state):
    """
    Generate an execution workflow for the current objective.

    The executor is responsible only for tactical workflow design.
    It does not execute capabilities or mutate runtime state.
    """

    execution_context = build_execution_context(
        state=state,
    )

    print("\n========== EXECUTION CONTEXT ==========")
    print(execution_context.model_dump())

    prompt = TERMINAL_EXECUTOR_PROMPT.format(
        **execution_context.model_dump()
    )

    # executor_output = call_ollama(
    #     prompt=prompt,
    #     model="qwen2.5-coder:7b",
    #     subagent=True,
    #     state_model=ExecutorOutput,
    # )

    executor_output = call_nvidia(
        prompt,
        "nvidia/nemotron-3-ultra-550b-a55b",
        subagent=True,
        state_model=ExecutorOutput,
    )
    runtime_state = state.get("runtime_state")
    if runtime_state is not None: 
        runtime_state.decision_context = None

    print("\n========== EXECUTOR ==========")
    print(executor_output.model_dump())

    return {
        "execution_workflow": executor_output.workflow,
    }