ALLOWED_ACTIONS = {
    "open_app",
    "focus_app",
    "type_text",
    "press_key",
    "hotkey"
}


def validate_plan(plan):

    if not isinstance(plan, list):
        return "invalid_format"

    for step in plan:

        # -------------------------
        # TOOL STEP
        # -------------------------
        if "tool" in step:

            if not isinstance(
                step["tool"],
                str
            ):
                return "invalid_tool"

            # actual tool existence
            # should be checked in
            # tool_router

            continue

        # -------------------------
        # ACTION STEP
        # -------------------------
        if "action" not in step:
            return "missing_action"

        action = step["action"]

        if action not in ALLOWED_ACTIONS:
            return "invalid_action"

        if (
            action == "focus_app"
            and "app" not in step
        ):
            return "missing_app"

        if (
            action == "open_app"
            and "app" not in step
        ):
            return "missing_app"

        if (
            action == "hotkey"
            and "keys" not in step
        ):
            return "missing_keys"

        if (
            action == "type_text"
            and "text" not in step
        ):
            return "missing_text"

        if (
            action == "press_key"
            and "key" not in step
        ):
            return "missing_key"

    return None