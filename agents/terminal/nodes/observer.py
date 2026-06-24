from agents.terminal.memory import artifact_store
from agents.terminal.state import TerminalState


def terminal_observer_node(state: TerminalState):

    print("\n[OBSERVATION]")
    print(state["compressed_observation"])

    if state.get("artifact_ids"):
        print(f"\nArtifacts: " f"{len(state['artifact_ids'])}")

    entry = f"""
ACTION TYPE:
{state["action_type"]}

THOUGHT:
{state["thought"]}

COMMAND:
{state["command"]}

OBSERVATION:
{state["compressed_observation"]}
"""
    artifact_ids = state.get("artifact_ids", [])

    if artifact_ids:

        entry += "\n\nARTIFACTS:\n"

        for artifact_id in artifact_ids:

            artifact = artifact_store.get(artifact_id)

            if artifact:

                entry += f"""
    ID: {artifact.artifact_id}
    TYPE: {artifact.artifact_type}
    SUMMARY: {artifact.summary}

    """

    updated_scratchpad = state.get("scratchpad", "") + "\n" + entry
    return {"scratchpad": updated_scratchpad, "step_count": state.get("step_count", 0) + 1}
