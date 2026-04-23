ALLOWED_ACTIONS = {"open_app", "type_text", "press_key"}

def validate_plan(plan):
    if not isinstance(plan, list):
        return "invalid_format"

    for step in plan:
        if "action" not in step:
            return "missing_action"

        if step["action"] not in ALLOWED_ACTIONS:
            return "invalid_action"

        if step["action"] == "open_app" and "app" not in step:
            return "missing_app"

        if step["action"] == "type_text" and "text" not in step:
            return "missing_text"

        if step["action"] == "press_key" and "key" not in step:
            return "missing_key"

    return None