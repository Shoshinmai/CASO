# from agents.terminal.models import TerminalAction
# from llm.llmclient import call_groq, call_ollama

# from agents.terminal.prompts.reasoner_prompt import TERMINAL_REASONER_PROMPT
# from agents.terminal.state import TerminalState
# from agents.terminal.memory import artifact_store


# def terminal_reasoner_node(state: TerminalState):

#     artifact_context = ""
#     for artifact in artifact_store.get_all():

#         artifact_context += f"""
# Artifact ID:
# {artifact.artifact_id}

# Type:
# {artifact.artifact_type}

# Summary:
# {artifact.summary}

# Created From:
# {artifact.metadata.get(
#     "command",
#     "Unknown"
# )}

# Original Goal:
# {artifact.metadata.get(
#     "goal",
#     "Unknown"
# )}

# Output Length:
# {artifact.metadata.get(
#     "output_length",
#     0
# )}
# --------------------------------
# """
#     print("\n[ARTIFACT CONTEXT]")
#     print(artifact_context)
#     ARTIFACT_USAGE = {
#         "file_listing": "find_file:<filename>",
#         "package_list": "find_package:<name>",
#         "log": "search_log:<query>",
#         "git_diff": "search_diff:<query>",
#         "command_output": "general retrieval",
#         "system_command": "commands for system manupulation.",
#     }

#     usage_hint = ARTIFACT_USAGE.get(state.get("artifact_type", ""), "unknown")

#     artifact_context += f"""

# Usage:
# {usage_hint}

# """
#     prompt = TERMINAL_REASONER_PROMPT.format(
#         goal=state.get("goal", ""),
#         scratchpad=state.get("scratchpad", ""),
#         artifact_context=artifact_context,
#         validation_error=state.get("validation_error", ""),
#         safety_reason=state.get("safety_reason", ""),
#     )

#     # response = call_ollama(prompt, "llama3.1:8b", True, TerminalAction)
#     response = call_ollama(prompt, "qwen2.5:7b-instruct-q3_K_M", tool=True)

#     # print("\n[REASONER]")

#     # print(f"\nACTION TYPE: " f"{response.action_type}")

#     # print(f"THOUGHT: " f"{response.thought}")

#     # if response.action_type == "tool_call":

#     #     print(f"TOOL: " f"{response.tool_name}")

#     #     print(f"INPUT: " f"{response.tool_input}")

#     # else:

#     #     print(f"COMMAND: " f"{response.command}")

#     strategy = build_strategy(response)

#     print("\n[CURRENT STRATEGY]")
#     print(strategy)

#     return {
#         "messages": [response],
#         "current_strategy": strategy,
#     }