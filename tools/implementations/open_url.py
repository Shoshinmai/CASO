from tools.base_tool import BaseTool


DEFAULT_BROWSER = "chrome"


class OpenUrlTool(BaseTool):

    name = "browser.open_url"

    description = (
        "Open a URL in the browser. "
        "If browser is already running, focus it. "
        "If browser is already focused, reuse it."
    )

    parameters = {
        "url": "string"
    }

    examples = [
        {
            "tool": "browser.open_url",
            "url": "https://youtube.com"
        },
        {
            "tool": "browser.open_url",
            "url": "https://github.com"
        }
    ]

    def execute(
        self,
        params,
        system_state
    ):

        url = params["url"]

        running_apps = [
            app.lower()
            for app in system_state.get(
                "running_apps",
                []
            )
        ]

        active_window = (
            system_state.get(
                "active_window"
            ) or ""
        ).lower()

        actions = []

        browser_running = (
            DEFAULT_BROWSER
            in running_apps
        )

        browser_focused = (
            DEFAULT_BROWSER
            in active_window
        )

        # Browser not running
        if not browser_running:

            actions.append(
                {
                    "action": "open_app",
                    "app": DEFAULT_BROWSER
                }
            )

        # Browser running but not focused
        elif not browser_focused:

            actions.append(
                {
                    "action": "focus_app",
                    "app": DEFAULT_BROWSER
                }
            )

        # Reuse focused browser
        actions.extend(
            [
                {
                    "action": "hotkey",
                    "keys": [
                        "ctrl",
                        "l"
                    ]
                },
                {
                    "action": "type_text",
                    "text": url
                },
                {
                    "action": "press_key",
                    "key": "enter"
                }
            ]
        )

        return actions