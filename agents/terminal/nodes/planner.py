from agents.terminal.models import ObservationDecision, PlanningOutput
from agents.terminal.prompts.planner_prompt import TERMINAL_PLANNER_PROMPT
from agents.terminal.tools import TOOLS
from agents.terminal.utils.capability_selector import get_candidate_tools
from agents.terminal.utils.tool_prompt_builder import build_capability_prompt
from llm.llmclient import call_nvidia, call_ollama


def terminal_planner_node(state):

    candidate_tools = get_candidate_tools(state)

    capability_prompt = build_capability_prompt(
        candidate_tools
    )
    print("\n========== CAPABILITY PROMPT ==========")
    print(capability_prompt)

    prompt = TERMINAL_PLANNER_PROMPT.format(
        goal=state["goal"],
        scratchpad=state.get("scratchpad", ""),
        artifact_context=state.get("artifact_context", ""),
        validation_error=state.get("validation_error", ""),
        safety_reason=state.get("safety_reason", ""),
        capabilities=capability_prompt,
    )

    # plan = call_ollama(
    #     prompt=prompt,
    #     # model="qwen2.5:7b-instruct-q3_K_M",
    #     model="freehuntx/qwen3-coder:8b ",
    #     subagent=True,
    #     state_model=PlanningOutput,
    # )
    plan = call_nvidia(prompt, "nvidia/nemotron-3-ultra-550b-a55b", subagent=True, state_model=PlanningOutput)
    print(PlanningOutput.model_json_schema())

    print("\n========== PLANNER ==========")
    print(plan.model_dump())
    print(type(plan))
    print(plan)

    return {
        "planner_output": plan,
    }

# state = {
#     "goal": "Locate llmclient.py",
#     "scratchpad": "",
#     "artifact_context": "",
#     "validation_error": "",
#     "safety_reason": "",
# }

# print(
#     terminal_planner_node(state)
# )