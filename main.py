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
from executor.executor import Executor
from intent.intent_extractor import extract_plan

if __name__ == "__main__":
    executor = Executor(delay=1.5)

    while True:
        user_input = input("\nEnter command: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        try:
            plan = extract_plan(user_input)
            print("\n[PLAN]")
            print(plan)

            executor.run(plan)

        except Exception as e:
            print(f"[ERROR] {str(e)}")