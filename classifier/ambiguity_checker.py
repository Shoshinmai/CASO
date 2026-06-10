from llm.llmclient import call_groq, call_ollama
from llm.prompts import AMBIGUITY_PROMPT

def check_ambiguity(user_input):

    prompt = f"""
{AMBIGUITY_PROMPT}

User:
{user_input}
"""

    return call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M").strip()
    # return call_groq(prompt).strip()