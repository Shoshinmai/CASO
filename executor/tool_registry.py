from executor.tools.open_app import open_app
from executor.tools.type_text import type_text
from executor.tools.press_key import press_key

ACTION_REGISTRY = {
    "open_app": open_app,
    "type_text": type_text,
    "press_key": press_key,
}