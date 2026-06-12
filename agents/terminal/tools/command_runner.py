import subprocess


def run_command(command: str):

    try:

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=15
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }

    except Exception as e:

        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": -1
        }