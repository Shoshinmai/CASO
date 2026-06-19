from agents.terminal.models import EvaluatorDecision
from agents.terminal.prompts.evaluator_prompt import TERMINAL_EVALUATOR_PROMPT
from agents.terminal.state import TerminalState
from llm.llmclient import call_groq, call_ollama


def terminal_evaluator_node(state: TerminalState):

    prompt = TERMINAL_EVALUATOR_PROMPT.format(
        goal=state["goal"],
        scratchpad=state.get("scratchpad", "")
    )

    response = call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M", True, EvaluatorDecision)

    print("\n[EVALUATOR]")
    print(response)

    return {
        "done":
            response.decision == "DONE"
    }