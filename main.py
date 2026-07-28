# # Executor testing
# from executor.executor import Executor

# if __name__ == "__main__":
#     executor = Executor(delay=1.5)

#     plan = [
#         {"action": "open_app", "app": "chrome"},
#         {"action": "type_text", "text": "youtube"},
#         {"action": "press_key", "key": "enter"},
#         # {"action": "type_text", "text": "/"},
#         {"action": "press_key", "key": "/"},
#         {"action": "type_text", "text": "anime"},
#         {"action": "press_key", "key": "enter"},
#     ]
#     # plan = [
#     #     {"action": "open_app", "app": "notepad"},
#     # ]

#     executor.run(plan)


#LLM testing with intention
# from executor.executor import Executor
# from intent.intent_extractor import extract_plan

# if __name__ == "__main__":
#     executor = Executor(delay=1.5)

#     while True:
#         user_input = input("\nEnter command: ")

#         if user_input.lower() in ["exit", "quit"]:
#             break

#         try:
#             plan = extract_plan(user_input)
#             print("\n[PLAN]")
#             print(plan)

#             executor.run(plan)

#         except Exception as e:
#             print(f"[ERROR] {str(e)}")


#Clarification Loop and state awareness testing
# from executor.executor import Executor
# from state.state_manager import get_system_state
# from core.kill_switch import (
#    start_kill_switch
# )

# from classifier.ambiguity_checker import (
#     check_ambiguity
# )

# from planner.plan_generator import generate_plan
# from planner.validator import validate_plan

# from critic.reviewer import review_plan

# from clarification.conversation_state import (
#     ConversationState
# )

# from clarification.resume_handler import (
#     merge_clarification
# )


# MAX_CLARIFICATIONS=2


# def main():

#     executor=Executor(delay=1.5)

#     state=ConversationState()
    
#     start_kill_switch()

#     print(
#     "Kill switch: Ctrl+Shift+X"
#     )


#     while True:

#         user_input=input(
#             "\nEnter command: "
#         ).strip()


#         if user_input.lower() in [
#             "exit",
#             "quit"
#         ]:
#             break


#         try:

#             # ------------------------
#             # clarification continuation
#             # ------------------------
#             if state.awaiting_clarification:

#                 user_input=merge_clarification(
#                     state.pending_original_request,
#                     state.pending_question,
#                     user_input
#                 )

#                 print(
#                   "\n[RECONSTRUCTED REQUEST]"
#                 )
#                 print(user_input)


#             # ------------------------
#             # ambiguity classifier
#             # ------------------------
#             ambiguity_result=check_ambiguity(
#                 user_input
#             )

#             print(
#                 "\n[INTERPRETER]"
#             )
#             print(
#                 ambiguity_result
#             )


#             if ambiguity_result.startswith(
#                 "AMBIGUOUS"
#             ):

#                 state.clarification_count +=1

#                 if (
#                    state.clarification_count
#                    >=MAX_CLARIFICATIONS
#                 ):

#                     print(
#                      "\nToo much ambiguity."
#                     )
#                     print(
#                      "Please rephrase request."
#                     )

#                     state.clear()

#                     continue


#                 question=(
#                     ambiguity_result
#                     .replace(
#                       "AMBIGUOUS:",
#                       ""
#                     )
#                     .strip()
#                 )


#                 print(
#                     "\n[CLARIFICATION]"
#                 )
#                 print(question)


#                 state.set_pending(
#                     user_input,
#                     question
#                 )

#                 continue


#             # resolved -> clear pending
#             if state.awaiting_clarification:
#                 state.clear()



#             # ------------------------
#             # planner
#             # ------------------------
#             system_state=get_system_state()

#             print(
#             "\n[SYSTEM STATE]"
#             )
#             print(system_state)

#             plan=generate_plan(
#             user_input,
#             system_state
#             )

#             print("\n[PLAN]")
#             print(plan)



#             # ------------------------
#             # deterministic validation
#             # ------------------------
#             issue=validate_plan(
#                 plan
#             )

#             if issue:
#                 print(
#                   f"[VALIDATION ERROR] {issue}"
#                 )
#                 continue



#             # ------------------------
#             # critic review
#             # ------------------------
#             critic_result=review_plan(
#                 user_input,
#                 plan
#             )

#             print(
#                 "\n[CRITIC]"
#             )
#             print(
#                critic_result
#             )


#             if (
#               critic_result.strip()
#               =="EXECUTE"
#             ):

#                 executor.run(
#                     plan
#                 )

#             else:
#                 state.set_pending(
#                     user_input,
#                     critic_result
#                 )
#                 print(
#                  "Critic rejected plan."
#                 )


#         except Exception as e:

#             print(
#               f"\n[ERROR] {e}"
#             )


# if __name__=="__main__":
#     main()


#Langgraph integration

from graph_.graph_builder import graph
from langgraph.types import Command

config = {"configurable": {"thread_id": "caso-3"}}
state = {}


while True:
    if not state:
        user_input = input("\nEnter command: ")
        state = {"user_input": user_input}

        result = graph.invoke(state, config=config)
    else:
        result = graph.invoke(
            Command(resume=state["user_clarification"]),
            config=config
        )

    if "__interrupt__" in result:
        interrupt_obj = result["__interrupt__"][0]
        question = interrupt_obj.value["question"]

        print(f"\n[CLARIFICATION] {question}")

        answer = input("→ ")

        state = {"user_clarification": answer}
        continue

    print("\n[DONE]")
    print(result)
    graph.checkpointer.delete_thread(thread_id="caso-3")
    state = {}