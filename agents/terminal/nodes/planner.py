from agents.terminal.memory import artifact_store
from agents.terminal.models import PlanningOutput, TaskPlanningOutput
from agents.terminal.prompts.planner_prompt import TERMINAL_PLANNER_PROMPT
from agents.terminal.utils.planner_context_builder import build_planner_context
from llm.llmclient import call_nvidia, call_ollama


def terminal_planner_node(state):

    planner_context = build_planner_context(
        state=state,
    )

    print("\n========== ACTIVE MEMORY ==========")
    print(planner_context["active_memory"])

    prompt = TERMINAL_PLANNER_PROMPT.format(**planner_context)


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
        state_model=TaskPlanningOutput,
    )

    print("\n========== PLANNER ==========")
    print(plan.model_dump())

    return {
        "planner_output": plan,
    }


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
