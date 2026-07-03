from langchain_core.messages import AIMessage

from agents.terminal.models import PlanningOutput
from agents.terminal.prompts.tool_compiler_prompt import (
    TOOL_SELECTOR_PROMPT,
)
from llm.llmclient import call_ollama


def terminal_tool_selector_node(state):
    
    print("\n===== TOOL SELECTOR STATE =====")
    print(state)
    print(type(state))
    print(state.get("planner_output"))

    plan = state["planner_output"].planning_step

    prompt = TOOL_SELECTOR_PROMPT.format(
        strategy=plan.strategy,
        capability=plan.capability,
        capability_input=plan.args,
    )

    response = call_ollama(
        prompt=prompt,
        model="qwen2.5:7b-instruct-q3_K_M",
        tool=True,
    )
    print("\n========== TOOL SELECTOR ==========")

    print(type(response))

    print()

    print(response)
    
    print("\n========== PLANNER OUTPUT ==========")
    print(plan.model_dump())

    print("\n========== TOOL CALL ==========")
    print(response.tool_calls)

    return {
        "messages": [response],
    }