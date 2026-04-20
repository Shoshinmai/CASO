import subprocess as sp
import os

def open_app(app: str):
    try:
        if app.lower() == "chrome":
            sp.Popen("start chrome", shell=True)
        elif app.lower() == "notepad":
            sp.Popen("notepad.exe")
        else:
            raise Exception(f"Unsupported app: {app}")
    except Exception as e:
        raise Exception(f"open_app failed: {str(e)}")

# open_app(input("Enter the name of the app: "))