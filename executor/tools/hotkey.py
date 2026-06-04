import pyautogui
# from sqlalchemy import True_

def hotkey(keys):
    if isinstance(keys, list):
        print(True)
        pyautogui.hotkey(*keys)
    else:
        keys = keys.split("+")
        print(keys)
        pyautogui.hotkey(*keys)