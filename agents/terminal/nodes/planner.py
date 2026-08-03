from agents.terminal.memory import artifact_store
from agents.terminal.models import PlanningOutput
from agents.terminal.prompts.planner_prompt import TERMINAL_PLANNER_PROMPT
from agents.terminal.utils.capability_selector import get_candidate_tools
from agents.terminal.utils.planner_context_builder import build_planner_context
from agents.terminal.utils.tool_prompt_builder import build_capability_prompt
from agents.terminal.utils.memory_formatter import (
    format_active_memory,
)
from llm.llmclient import call_nvidia, call_ollama


def terminal_planner_node(state):

    candidate_tools = get_candidate_tools(state)
    
    capability_prompt = build_capability_prompt(candidate_tools)

    planner_context = build_planner_context(
        state=state,
        capability_prompt=capability_prompt,
    )

    print("\n========== ACTIVE MEMORY ==========")
    print(planner_context["active_memory"])

    prompt = TERMINAL_PLANNER_PROMPT.format(
        **planner_context
    )

#     capability_prompt = build_capability_prompt(candidate_tools)
#     artifact_context = build_artifact_context(state.get("artifact_ids", []))
#     runtime_memory = format_active_memory(
#         active_memory=state["active_memory"],
#         # execution_memory=state["execution_memory"],
#         # thread_memory=state["thread_memory"],
#     )
#     print("\n========== ACTIVE MEMORY ==========")
#     print(runtime_memory)
#     # print("\n========== CAPABILITY PROMPT ==========")
#     # print(capability_prompt)
#     active_memory_context = format_active_memory(
#     state["active_memory"]
# )

#     execution_history = state.get("scratchpad", "")
        
#     print("\n[PLANNER CONTEXT]")
#     print(active_memory_context)
    
#     prompt = TERMINAL_PLANNER_PROMPT.format(
#         goal=state["task"].goal,
#         scratchpad=active_memory_context,
#         artifact_context=artifact_context,
#         validation_error=state.get("validation_error", ""),
#         safety_reason=state.get("safety_reason", ""),
#         capabilities=capability_prompt,
#     )

    # plan = call_ollama(
    #     prompt=prompt,
    #     model="qwen2.5-coder:7b",
    #     # model="freehuntx/qwen3-coder:8b ",
    #     subagent=True,
    #     state_model=PlanningOutput,
    # )
    plan = call_nvidia(
        prompt,
        "nvidia/nemotron-3-ultra-550b-a55b",
        subagent=True,
        state_model=PlanningOutput,
    )
    # print(PlanningOutput.model_json_schema())

    print("\n========== PLANNER ==========")
    print(plan.model_dump())
    # print(type(plan))
    # print(plan)

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


def build_artifact_context(
    artifact_ids: list[str] | None,
) -> str:
    """
    Build compact planner-facing context for available artifacts.
    """

    if not artifact_ids:
        return "No artifacts available."

    catalog = artifact_store.get_catalog(artifact_ids=artifact_ids)

    if not catalog:
        return "No artifacts available."

    sections = []

    for artifact in catalog:
        sections.append(
            "\n".join(
                [
                    f"Artifact ID: {artifact['artifact_id']}",
                    f"Type: {artifact['artifact_type']}",
                    f"Summary: {artifact['summary']}",
                ]
            )
        )

    return "\n\n".join(sections)
