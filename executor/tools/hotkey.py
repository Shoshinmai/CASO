import pyautogui

def hotkey(keys):
    keys = keys.split("+")
    pyautogui.hotkey(*keys)