from llm.llmclient import call_groq
from llm.parser import parse_llm_output
from llm.prompts import SYSTEM_PROMPT

def generate_plan(user_input: str):
    prompt = SYSTEM_PROMPT + f"\nUser: {user_input}\nOutput:"
    
    raw = call_groq(prompt)
    print("\n[LLM RAW PLAN]")
    print(raw)

    return parse_llm_output(raw)