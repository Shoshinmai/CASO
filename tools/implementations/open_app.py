from tools.base_tool import BaseTool


class OpenAppTool(BaseTool):

    name = "desktop.open_app"

    description = (
        "Open an application or focus it if already running."
    )

    parameters = {
        "app": "string"
    }

    def execute(
        self,
        params,
        system_state
    ):

        app = params["app"].lower()

        running_apps = [
            a.lower()
            for a in system_state.get(
                "running_apps",
                []
            )
        ]

        if app in running_apps:

            return [
                {
                    "action": "focus_app",
                    "app": app
                }
            ]

        return [
            {
                "action": "open_app",
                "app": app
            }
        ]