from executor.executor import Executor

if __name__ == "__main__":
    executor = Executor(delay=1)

    plan = [
        {"action": "open_app", "app": "chrome"},
        {"action": "type_text", "text": "youtube"},
        {"action": "press_key", "key": "enter"},
        {"action": "type_text", "text": "/"},
        {"action": "type_text", "text": "anime"},
        {"action": "press_key", "key": "enter"},
    ]

    executor.run(plan)