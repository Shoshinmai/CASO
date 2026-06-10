from llm.llmclient import call_groq, call_ollama
from llm.prompts import MERGE_PROMPT


def merge_clarification(
    original,
    question,
    answer
):
    prompt = MERGE_PROMPT.format(
        original=original,
        question=question,
        answer=answer
    )

    # response = call_groq(prompt)
    response = call_ollama(prompt, "phi4-mini:latest")

    return response.strip()