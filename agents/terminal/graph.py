from langgraph.graph import StateGraph, END

from agents.terminal.nodes.compressor import terminal_compressor_node
from agents.terminal.nodes.evaluator import terminal_evaluator_node
from agents.terminal.nodes.validator import command_validator_node
from agents.terminal.router.evaluator_router import evaluator_router
from agents.terminal.router.safety_router import safety_router
from agents.terminal.router.validator_router import validator_router
from agents.terminal.state import TerminalState

from agents.terminal.nodes.reasoner import terminal_reasoner_node

from agents.terminal.nodes.safety import safety_filter_node

from agents.terminal.nodes.executor import terminal_executor_node

from agents.terminal.nodes.observer import terminal_observer_node

builder = StateGraph(TerminalState)

builder.add_node("reasoner", terminal_reasoner_node)

builder.add_node("safety_filter", safety_filter_node)

builder.add_node("executor", terminal_executor_node)

builder.add_node("observer", terminal_observer_node)
builder.add_node("evaluator", terminal_evaluator_node)
builder.add_node("validator", command_validator_node)
builder.add_node("compressor", terminal_compressor_node)

builder.set_entry_point("reasoner")
builder.add_edge("reasoner", "validator")
builder.add_conditional_edges(
    "validator",
    validator_router,
    {"safety_filter": "safety_filter", "reasoner": "reasoner"},
)

builder.add_conditional_edges(
    "safety_filter", safety_router, {"executor": "executor", END: END}
)
builder.add_edge("executor", "compressor")
builder.add_edge("compressor", "observer")
builder.add_edge("observer", "evaluator")
builder.add_conditional_edges(
    "evaluator", evaluator_router, {"reasoner": "reasoner", END: END}
)

terminal_graph = builder.compile()
