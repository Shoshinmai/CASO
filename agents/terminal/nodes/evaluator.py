from agents.terminal.models import EvaluatorDecision
import json
from agents.terminal.prompts.evaluator_prompt import TERMINAL_EVALUATOR_PROMPT
from agents.terminal.state import TerminalState
from llm.llmclient import call_groq, call_ollama


def terminal_evaluator_node(state: TerminalState):

    observation = state["observation_input"]
    planner_output = state.get("planner_output")

    strategy = ""

    if planner_output is not None:
        strategy = planner_output.planning_step.strategy
    latest_result = observation.raw_result

    if isinstance(latest_result, dict):
        latest_result = json.dumps(latest_result, indent=2)

    prompt = TERMINAL_EVALUATOR_PROMPT.format(
        goal=state["goal"],
        strategy=strategy,
        scratchpad=state.get("scratchpad", ""),
        latest_tool=observation.tool_name,
        latest_result=latest_result,
    )
    print("\n[CURRENT STRATEGY]")
    print(strategy)

    print("\n[LATEST TOOL]")
    print(observation.tool_name)

    print("\n[LATEST TOOL RESULT]")
    print(latest_result)

    response = call_ollama(
        prompt, "qwen2.5:7b-instruct-q3_K_M", True, EvaluatorDecision
    )
    # response = call_ollama(prompt, "llama3.1:8b", True, EvaluatorDecision)

    print("\n[EVALUATOR]")
    print(f"Scratchpad: {state.get("scratchpad", "")}")
    print(response)

    return {"done": response.decision == "DONE"}
