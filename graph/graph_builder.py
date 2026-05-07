from langgraph.graph import StateGraph, END
from graph.states import AgentState
from graph.wrappers import state_node, ambiguity_node, planner_node, validator_node, critic_node, executor_node
from graph.routers import route_after_critic, route_after_validator
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()

builder = StateGraph(AgentState)

builder.add_node("state", state_node)
builder.add_node("ambiguity", ambiguity_node)
builder.add_node("planner", planner_node)
builder.add_node("validator", validator_node)
builder.add_node("critic", critic_node)
builder.add_node("executor", executor_node)

builder.set_entry_point("state")

builder.add_edge("state", "ambiguity")
builder.add_edge("ambiguity", "planner")
builder.add_edge("planner", "validator")

builder.add_conditional_edges(
    "validator",
    route_after_validator,
    {
        "invalid": END,
        "critic": "critic"
    }
)

builder.add_conditional_edges(
    "critic",
    route_after_critic,
    {
        "ambiguity": "ambiguity",
        "planner": "planner",
        "executor": "executor"
    }
)

builder.add_edge("executor", END)

graph = builder.compile(checkpointer=checkpointer)