from agents.terminal.critics.context_builder import (
    build_critic_context,
)
from agents.terminal.critics.models import CriticOutput
from agents.terminal.prompts.critics_prompt import TERMINAL_CRITIC_PROMPT
from llm.llmclient import call_nvidia


def terminal_critic_node(state):
    """
    Evaluate the current task objective and produce a
    structured CriticOutput.

    The Critic only evaluates and recommends.
    It does not execute the resulting decision.
    """

    critic_context = build_critic_context(
        state=state,
    )

    print("\n========== CRITIC CONTEXT ==========")
    print(critic_context.model_dump())

    prompt = TERMINAL_CRITIC_PROMPT.format(
        **critic_context.model_dump()
    )

    critic_output = call_nvidia(
        prompt,
        "nvidia/nemotron-3-ultra-550b-a55b-16k",
        subagent=True,
        state_model=CriticOutput,
    )

    print("\n========== CRITIC ==========")
    print(critic_output.model_dump())

    return {
        "critic_output": critic_output,
    }