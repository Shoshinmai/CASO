from agents.terminal.models import TerminalAction
from llm.llmclient import call_groq, call_ollama

from agents.terminal.prompts.reasoner_prompt import TERMINAL_REASONER_PROMPT
from agents.terminal.state import TerminalState


def terminal_reasoner_node(state: TerminalState):

    prompt = TERMINAL_REASONER_PROMPT.format(
        goal=state.get("goal", ""),
        scratchpad=state.get("scratchpad", ""),
        validation_error=state.get("validation_error", ""),
        safety_reason=state.get("safety_reason", "")
    )

    response = call_ollama(prompt, "freehuntx/qwen3-coder:8b", True, TerminalAction)

    print("\n[REASONER]")
    print(f"\nTHOUGHT: {response.thought}")
    print(f"COMMAND: {response.command}")

    return {
        "thought": response.thought,
        "command": response.command
    }
