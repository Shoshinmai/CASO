import keyboard
import threading

import core.control_flags as flags


def trigger_abort():

    flags.STOP_EXECUTION = True

    print(
      "\n[EMERGENCY STOP TRIGGERED]"
    )


def start_kill_switch():

    keyboard.add_hotkey(
        "ctrl+shift+x",
        trigger_abort
    )

    listener=threading.Thread(
        target=keyboard.wait,
        daemon=True
    )

    listener.start()