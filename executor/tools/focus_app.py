import win32gui
import win32process
import psutil
import pyautogui
import time


APP_PROCESS={
 "chrome":"chrome.exe",
 "vscode":"Code.exe",
 "notepad":"notepad.exe"
}


def focus_app(app):

    target=APP_PROCESS.get(
       app.lower()
    )

    if not target:
        raise Exception(
          "unknown app"
        )


    pids=[]

    for proc in psutil.process_iter(
       ['pid','name']
    ):
        try:
            # print(f"apps--> {proc}")
            if proc.info["name"].lower()==target:
                pids.append(
                    proc.info["pid"]
                )
        except:
            pass

    print(f"PIDS--> {pids}")
    if not pids:
        raise Exception(
           f"{app} not running"
        )



    def enum_handler(hwnd,_):

        if not win32gui.IsWindowVisible(
            hwnd
        ):
            return


        _,pid=(
         win32process
         .GetWindowThreadProcessId(
             hwnd
         )
        )


        if pid in pids:

            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd,9)
                time.sleep(0.2)

            pyautogui.keyDown(
               "alt"
            )
            pyautogui.keyUp(
               "alt"
            )

            time.sleep(0.2)

            win32gui.SetForegroundWindow(
                hwnd
            )

            raise StopIteration



    try:
        win32gui.EnumWindows(
          enum_handler,
          None
        )

    except StopIteration:

        return {
          "status":"success",
          "action":"focus_app"
        }


    raise Exception(
      "No window found"
    )

# focus_app("chrome")