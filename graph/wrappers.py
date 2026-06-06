from graph.states import AgentState
from langgraph.types import interrupt
from classifier.ambiguity_checker import check_ambiguity
from state.state_manager import get_system_state
from planner.plan_generator import generate_plan
from planner.validator import validate_plan
from critic.reviewer import review_plan
from executor.executor import Executor
from clarification.resume_handler import merge_clarification
from tools.router import execute_tool

def state_node(state: AgentState):
    return {
        "system_state": get_system_state()
    }

def ambiguity_node(state: AgentState):
    result = check_ambiguity(state["user_input"])

    if result.startswith("AMBIGUOUS"):
        question = result.replace("AMBIGUOUS:", "").strip()

        # 🔥 pause execution
        answer = interrupt({"question": question})

        merged = merge_clarification(
            state["user_input"],
            question,
            answer
        )

        return {"user_input": merged, "ambiguity_decision": question}
    else:
        return {"ambiguity_decision": "CLEAR"}


def planner_node(state: AgentState):

    plan = generate_plan(
        user_input=state["user_input"],
        system_state=state["system_state"],
        critic_feedback=state.get(
            "critic_feedback"
        ),
        previous_plan=state.get("plan")
    )

    return {
        "plan": plan
    }

def validator_node(state: AgentState):
    issue = validate_plan(state["plan"])
    return {"validation_error": issue}

def critic_node(state: AgentState):

    decision = review_plan(
        state["user_input"],
        state["plan"]
    ).strip()

    print("\n[CRITIC DECISION]")
    print(decision)

    # --------------------------------
    # CLARIFICATION
    # --------------------------------
    if decision.startswith("CLARIFY:"):

        question = (
            decision
            .replace("CLARIFY:", "")
            .strip()
        )

        answer = interrupt({
            "question": question
        })

        merged = merge_clarification(
            state["user_input"],
            question,
            answer
        )

        return {
            "user_input": merged,
            "critic_decision": "RETRY"
        }

    # --------------------------------
    # REVISE PLAN
    # --------------------------------
    if decision.startswith("REVISE_PLAN:"):

        count = state.get(
            "revise_count",
            0
        ) + 1

        # 🔥 loop protection
        if count > 2:

            print(
                "\n[REVISE LIMIT REACHED]"
            )

            return {
                "critic_decision": "EXECUTE",
                "revise_count": count
            }

        feedback = (
            decision
            .replace("REVISE_PLAN:", "")
            .strip()
        )

        return {
            "critic_decision": "REVISE",
            "critic_feedback": feedback,
            "revise_count": count
        }

    # --------------------------------
    # EXECUTE
    # --------------------------------
    return {
        "critic_decision": "EXECUTE"
    }
    
def executor_node(state: AgentState):
    result = Executor().run(state["plan"])
    return {"execution_result": result}

def tool_router_node(state):

    expanded_plan = []

    for step in state["plan"]:

        if "tool" not in step:

            expanded_plan.append(step)
            continue

        actions = execute_tool(
            tool_name=step["tool"],
            params=step,
            system_state=state["system_state"]
        )

        expanded_plan.extend(actions)

    return {
        "plan": expanded_plan
    }