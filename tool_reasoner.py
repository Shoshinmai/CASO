from llm.llmclient import call_ollama

from agents.terminal.prompts.reasoner_prompt import TERMINAL_REASONER_PROMPT


prompt = TERMINAL_REASONER_PROMPT.format(
    goal="Find llmclient.py",
    scratchpad="",
    artifact_context="",
    validation_error="",
    safety_reason="",
)

response = call_ollama(
    prompt=prompt,
    model="qwen2.5:7b-instruct-q3_K_M",
    tool=True,
)

print("\n========== RESPONSE TYPE ==========")
print(type(response))

print("\n========== AI MESSAGE ==========")
print(response)

print("\n========== CONTENT ==========")
print(response.content)

print("\n========== TOOL CALLS ==========")
print(response.tool_calls)

print("\n========== INVALID TOOL CALLS ==========")
print(response.invalid_tool_calls)