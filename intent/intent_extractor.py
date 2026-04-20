from llm.llmclient import call_gemini
from llm.prompts import SYSTEM_PROMPT
from llm.parser import parse_llm_output

def extract_plan(user_input: str):
    prompt = SYSTEM_PROMPT + f"\nUser: {user_input}\nOutput:"
    
    raw_output = call_gemini(prompt)
    
    print("\n[LLM RAW OUTPUT]")
    print(raw_output)

    plan = parse_llm_output(raw_output)

    return plan