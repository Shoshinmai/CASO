from llm.llmclient import call_gemini, call_groq
from llm.parser import parse_llm_output
from llm.prompts import SYSTEM_PROMPT


def generate_plan(
    user_input,
    system_state
):

    prompt=f"""
{SYSTEM_PROMPT}

Current System State:
{system_state}

User Request:
{user_input}
"""

    raw=call_groq(
       prompt
    )

    print(
      "\n[LLM RAW PLAN]"
    )
    print(raw)

    return parse_llm_output(
        raw
    )