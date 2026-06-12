ALLOWED_WINDOWS_COMMANDS = {
    "dir",
    "cd",
    "where python",
    "git status",
    "git branch",
    "python --version",
    "pip list"
}

def validate_command(command: str):

    if not command:
        return False

    first_token = command.split()[0].lower()

    return first_token in ALLOWED_WINDOWS_COMMANDS