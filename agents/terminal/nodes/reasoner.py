from agents.terminal.models import TerminalAction
from llm.llmclient import call_groq, call_ollama

from agents.terminal.prompts.reasoner_prompt import TERMINAL_REASONER_PROMPT
from agents.terminal.state import TerminalState
from agents.terminal.memory import artifact_store


def terminal_reasoner_node(state: TerminalState):

    artifact_context = ""
    for artifact in artifact_store.get_all():

        artifact_context += f"""
Artifact ID: {artifact.artifact_id}
Type: {artifact.artifact_type}
Summary: {artifact.summary}

"""
    print("\n[ARTIFACT CONTEXT]")
    print(artifact_context)
    prompt = TERMINAL_REASONER_PROMPT.format(
        goal=state.get("goal", ""),
        scratchpad=state.get("scratchpad", ""),
        artifact_context=artifact_context,
        validation_error=state.get("validation_error", ""),
        safety_reason=state.get("safety_reason", ""),
    )

    response = call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M", True, TerminalAction)

    print("\n[REASONER]")
    print(f"\nACTION TYPE: {response.action_type}")
    print(f"\nTHOUGHT: {response.thought}")
    print(f"COMMAND: {response.command}")

    return {
        "action_type": response.action_type,
        "thought": response.thought,
        "command": response.command,
    }
