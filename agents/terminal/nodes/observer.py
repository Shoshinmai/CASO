from agents.terminal.state import TerminalState


def terminal_observer_node(state: TerminalState):

    print("\n[OBSERVATION]")
    print(state["compressed_observation"])

    entry = f"""
THOUGHT:
{state['thought']}

COMMAND:
{state['command']}

OBSERVATION:
{state["compressed_observation"]}
"""

    return {

        "scratchpad":
            state.get("scratchpad", "") + "\n" + entry,

        "step_count":
            state.get("step_count", 0) + 1
    }