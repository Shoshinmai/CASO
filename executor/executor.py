from executor.tool_registry import ACTION_REGISTRY
import time


class Executor:
    def __init__(self, delay: float = 1.5):
        self.registry = ACTION_REGISTRY
        self.delay = delay

    def validate_action(self, action: dict):
        if "action" not in action:
            raise ValueError("Missing 'action' field")

        if action["action"] not in self.registry:
            raise ValueError(f"Unknown action: {action['action']}")

    def execute_step(self, action: dict):
        self.validate_action(action)

        action_name = action["action"]
        func = self.registry[action_name]

        # Remove 'action' key before passing args
        # params = {k: v for k, v in action.items() if k != "action"}
        params = {k: v for k, v in action.items() if k not in ["action", "intent"]}

        try:
            func(**params)
            return {"status": "success", "action": action_name}
        except Exception as e:
            return {"status": "error", "action": action_name, "message": str(e)}

    def run(self, plan: list):
        results = []

        for step in plan:
            result = self.execute_step(step)
            results.append(result)

            print(f"[EXECUTOR] {result}")

            if result["status"] == "error":
                print("[EXECUTOR] Stopping due to failure.")
                break

            time.sleep(self.delay)

        return results
