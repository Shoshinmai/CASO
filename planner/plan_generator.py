# from llm.llmclient import call_gemini, call_groq
# from llm.parser import parse_llm_output

import json

from llm.llmclient import call_groq, call_ollama
from planner.prompt_builder import build_planner_prompt


def generate_plan(user_input, system_state, critic_feedback=None, previous_plan=None):

    revise_section = ""

    # 🔥 include revise context ONLY if present
    if critic_feedback and previous_plan:

        revise_section = f"""

--------------------------------
PREVIOUS PLAN
--------------------------------
{json.dumps(previous_plan, indent=2)}

--------------------------------
CRITIC FEEDBACK
--------------------------------
{critic_feedback}

Improve the previous plan using the critic feedback.
Do NOT repeat the same mistakes.
"""

    prompt = build_planner_prompt(system_state)
    prompt += f"""

--------------------------------
USER REQUEST
--------------------------------
{user_input}

{revise_section}

--------------------------------
STRICT OUTPUT FORMAT
--------------------------------

Return ONLY valid JSON list.

Examples:

[
  {{
    "tool":"desktop.open_app",
    "app":"chrome"
  }}
]

[
  {{
    "action":"focus_app",
    "app":"chrome"
  }}
]

No markdown.
No explanation.
"""

    # raw = call_ollama(prompt, "qwen3:8b")
    raw = call_groq(prompt)

    print("\n[LLM RAW PLAN]")
    print(raw)

    # 🔥 strict extraction
    try:

        start = raw.find("[")
        end = raw.rfind("]") + 1

        json_str = raw[start:end]

        plan = json.loads(json_str)

        if not isinstance(plan, list):
            raise ValueError("Plan is not a list")

        return plan

    except Exception as e:

        print("\n[PLAN PARSE ERROR]")
        print(e)

        return []
