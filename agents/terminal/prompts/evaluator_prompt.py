TERMINAL_EVALUATOR_PROMPT = """
Reasoning budget: LOW.
Goal:
{goal}

History:
{scratchpad}

Has the goal been achieved?

Return valid JSON:

{{
    "decision": "DONE"
}}

or

{{
    "decision": "CONTINUE"
}}
"""