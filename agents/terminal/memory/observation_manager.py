import json
from agents.terminal.memory import artifact_store
from agents.terminal.models import ObservationDecision
from agents.terminal.prompts.observation_prompt import OBSERVATION_ANALYZER_PROMPT
from llm.llmclient import call_nvidia, call_ollama


def analyze_observation(state):

    observation = state["observation_input"]

    output = observation.raw_result

    if isinstance(output, dict):
        output = json.dumps(output, indent=2)

    prompt = OBSERVATION_ANALYZER_PROMPT.format(
        command=observation.tool_name,
        output_length=len(output),
        output_preview=output[:2000],
    )
    # res = call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M", subagent=True, state_model=ObservationDecision)
    res = call_nvidia(prompt, "qwen/qwen3.5-122b-a10b", subagent=True, state_model=ObservationDecision)
    
    print("\n========== RAW RESPONSE ==========")
    print(res)
     
    return res


def observation_manager_node(state):

    decision = analyze_observation(state)
    
    print("\n[OBSERVATION DECISION]")
    print(decision.model_dump())
    print("summary:", repr(decision.summary))
    print("conclusion:", repr(decision.conclusion))
    print("\n[MEMORY STRATEGY]")
    print(decision.memory_strategy)
    print("\n[OBSERVATION REASONING]")
    print(decision.reasoning)
    observation = state["observation_input"]
    output = observation.raw_result

    if isinstance(output, dict):
        output = json.dumps(output, indent=2)

    if decision.memory_strategy in ("store_artifact", "store_and_summarize"):
        artifact_id = artifact_store.save(
            artifact_type=decision.artifact_type,
            summary=decision.summary,
            data=observation.raw_result,
            metadata={
                "goal": state["goal"],
                "command": observation.tool_name,
                "output_length": len(output),
            },
        )
        existing = state.get("artifact_ids", [])

        updated = existing + [artifact_id]

        observation_ana = decision.summary

        if decision.important_information:

            observation_ana += f"""

IMPORTANT:
{decision.important_information}
"""
        return {
            "compressed_observation": observation_ana,
            "observation_summary": decision.summary,
            "observation_conclusion": decision.conclusion,
            "artifact_ids": updated,
        }

    if decision.memory_strategy == "pass_through":
        return {
            "compressed_observation": output,
            "observation_summary": decision.summary,
            "observation_conclusion": decision.conclusion,
        }

    if decision.memory_strategy == "discard":

        return {
            "compressed_observation": "Output discarded.",
            "observation_summary": "",
            "observation_conclusion": "",
        }

    return {
        "compressed_observation": observation.raw_result,
        "observation_summary": decision.summary,
        "observation_conclusion": decision.conclusion,
    }
