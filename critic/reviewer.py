from llm.llmclient import call_groq
from llm.prompts import CRITIC_PROMPT


VALID_PREFIXES = (
    "EXECUTE",
    "CLARIFY:",
    "REVISE_PLAN:"
)


def review_plan(user_input, plan):

    prompt = CRITIC_PROMPT.format(
        user_input=user_input,
        plan=plan
    )

    response = call_groq(prompt).strip()

    print("\n[CRITIC RAW]")
    print(response)

    # normalize
    response = response.strip()

    # validate structure
    if not response.startswith(VALID_PREFIXES):
        print("\n[CRITIC FORMAT ERROR]")
        print("Fallback → EXECUTE")

        return "EXECUTE"

    return response