from executor.tools.open_app import open_app
from executor.tools.type_text import type_text
from executor.tools.press_key import press_key
from executor.tools.hotkey import hotkey
from executor.tools.focus_app import focus_app

ACTION_REGISTRY = {
    "open_app": open_app,
    "focus_app": focus_app,
    "type_text": type_text,
    "press_key": press_key,
    "hotkey": hotkey,
}

TOOLS = {

 "open_app": open_app,

 "focus_app": focus_app,

 "type_text": type_text,

 "press_key": press_key,

 "hotkey": hotkey
}