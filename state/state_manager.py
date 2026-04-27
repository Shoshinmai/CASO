import psutil
import pygetwindow as gw


TARGET_APPS = {
    "chrome.exe": "chrome",
    "Code.exe": "vscode",
    "notepad.exe": "notepad"
}


def get_running_apps():

    apps=[]

    for proc in psutil.process_iter(
        ['name']
    ):
        try:
            name=proc.info['name']
            if name.lower() in TARGET_APPS:
                # print(f"Runinng app --> {name.lower()}")
                apps.append(
                    TARGET_APPS[name.lower()]
                )
                # print(f"Appending:-> {apps}")

        except:
            continue
    # print("DND")
    # print(apps)
    return list(
        set(apps)
    )


def get_system_state():

    try:
        win=gw.getActiveWindow()

        title=(
            win.title
            if win
            else None
        )

        return {
            "active_window": title,
            "running_apps": get_running_apps()
        }

    except:

        return {
            "active_window":None,
            "running_apps":[]
        }
        
# print(get_running_apps())
# print(get_system_state())