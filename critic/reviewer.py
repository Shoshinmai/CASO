from llm.llmclient import call_groq
from llm.prompts import CRITIC_PROMPT


def review_plan(user_input, plan):
    prompt = f"""
{CRITIC_PROMPT}

User Request:
{user_input}

Plan:
{plan}
"""

    response = call_groq(prompt).strip()

    return response
