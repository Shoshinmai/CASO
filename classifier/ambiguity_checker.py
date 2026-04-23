from llm.llmclient import call_groq
from llm.prompts import AMBIGUITY_PROMPT

def check_ambiguity(user_input):

    prompt = f"""
{AMBIGUITY_PROMPT}

User:
{user_input}
"""

    return call_groq(prompt).strip()