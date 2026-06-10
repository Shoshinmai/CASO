from llm.llmclient import call_groq, call_ollama
from llm.prompts import CRITIC_PROMPT
import json

from llm.prompts import CRITIC_PROMPT

from tools.registry import list_tools

VALID_PREFIXES = ("EXECUTE", "CLARIFY:", "REVISE_PLAN:")


def build_critic_prompt(user_input, plan):

    tool_blocks = []

    for tool in list_tools().values():

        tool_blocks.append(
            f"""
Tool:
{tool.name}

Description:
{tool.description}

Parameters:
{json.dumps(tool.parameters, indent=2)}

Examples:
{json.dumps(tool.examples, indent=2)}
"""
        )

    return CRITIC_PROMPT.format(
        user_input=user_input,
        plan=json.dumps(plan, indent=2),
        available_tools="\n".join(tool_blocks),
    )


def review_plan(user_input, plan):

    # print("\n[CRITIC INPUT PLAN]")
    # print(plan)
    prompt = build_critic_prompt(user_input, plan)

    response = call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M").strip()
    # response = call_groq(prompt).strip()

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