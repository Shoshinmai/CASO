from langgraph.graph import StateGraph, END

from agents.terminal.nodes.critic import terminal_critic_node
from agents.terminal.nodes.safety import safety_filter_node
from agents.terminal.router.critic_router import critic_router
from agents.terminal.router.safety_router import safety_router
from agents.terminal.state import TerminalState

from agents.terminal.nodes.planner import terminal_planner_node

from agents.terminal.nodes.validator import validate_command

from agents.terminal.nodes.executor import terminal_executor_node

from agents.terminal.nodes.observer import terminal_observer_node


# def validator_router(state):

#     if validate_command(
#         state["command"]
#     ):
#         return "executor"

#     return END


builder = StateGraph(TerminalState)

builder.add_node("planner", terminal_planner_node)

builder.add_node("safety_filter", safety_filter_node)

builder.add_node("critic", terminal_critic_node)

builder.add_node("executor", terminal_executor_node)

builder.add_node("observer", terminal_observer_node)

builder.set_entry_point("planner")
builder.add_edge(
    "planner",
    "safety_filter"
)
builder.add_conditional_edges(
    "safety_filter",
    safety_router,
    {
        "critic": "critic",
        "end": END
    }
)
builder.add_conditional_edges(
    "critic",
    critic_router,
    {
        "executor": "executor",
        END: END
    }
)

builder.add_edge("executor", "observer")

builder.add_edge("observer", END)

terminal_graph = builder.compile()
