from agents.terminal.models import FAKE_MODEL
from llm.llmclient import call_ollama

prompt = """[SYSTEM INSTRUCTION]
You are operating in an EMERGENCY low-latency mode. 
DO NOT use your internal thinking process. 
DO NOT produce a chain of thought. 
Output your final JSON response IMMEDIATELY.

========USER REQUEST=========

hi, who are you?
"""

print(call_ollama(prompt, "deepseek-r1:8b", True, state_model=FAKE_MODEL, tool=False ))