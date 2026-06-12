from agents.terminal.prompts.critic_prompt import TERMINAL_CRITIC_PROMPT
from llm.llmclient import call_groq

def terminal_critic_node(state):

    prompt = TERMINAL_CRITIC_PROMPT.format(
        goal=state["goal"],
        command=state["command"]
    )

    response = call_groq(
        prompt
    ).strip()

    print("\n[TERMINAL CRITIC]")
    print(response)

    if response == "EXECUTE":

        return {
            "critic_decision": "EXECUTE",
            "critic_feedback": ""
        }

    return {
        "critic_decision": "REVISE",
        "critic_feedback": response
    }