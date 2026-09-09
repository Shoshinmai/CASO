from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path


class ConcurrentDebugSession:
    """
    Temporary debugging instrumentation for the concurrent executor.

    This does NOT execute tasks.

    It only:
    - creates per-task debug logs
    - opens one Windows Terminal tab per task
    - records worker lifecycle events
    - lets the original PowerShell tab remain the controller

    Remove this helper after the async-IO migration debugging phase.
    """

    def __init__(
        self,
        *,
        plan_id: str,
        tasks,
    ) -> None:

        self.plan_id = plan_id

        self.run_id = f"{plan_id}-" f"{uuid.uuid4().hex[:8]}"

        self.root = Path(tempfile.gettempdir()) / "caso_concurrent_debug" / self.run_id

        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._locks: dict[str, threading.Lock] = {}

        for task in tasks:
            self._locks[task.task_id] = threading.Lock()

    def log_path(
        self,
        task_id: str,
    ) -> Path:

        safe_task_id = task_id.replace("/", "_").replace("\\", "_").replace(":", "_")

        return self.root / f"{safe_task_id}.jsonl"

    def open_worker_tab(
        self,
        *,
        task_id: str,
    ) -> None:

        log_path = self.log_path(task_id)

        python_executable = Path(
            sys.executable
        ).resolve()

        module = (
            "agents.terminal.runtime.debug_worker_tab"
        )

        # ----------------------------------------------------------
        # Resolve the CASO project root from this source file.
        #
        # concurrent_debug.py:
        #
        #   <project_root>
        #       agents/
        #           terminal/
        #               runtime/
        #                   concurrent_debug.py
        #
        # parents[3] -> <project_root>
        # ----------------------------------------------------------

        project_root = (
            Path(__file__)
            .resolve()
            .parents[3]
        )

        # ----------------------------------------------------------
        # Create a dedicated PowerShell launcher script.
        #
        # We intentionally do NOT pass the Python command through
        # wt.exe's -Command argument.
        #
        # Windows Terminal has its own command-line parser and the
        # nested PowerShell command was being interpreted incorrectly,
        # producing:
        #
        #     0x80070002
        #
        # Using -File gives PowerShell ownership of the script and
        # completely avoids that parsing problem.
        # ----------------------------------------------------------

        launcher_dir = (
            self.root / "_worker_launchers"
        )

        launcher_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        launcher_path = (
            launcher_dir
            / f"{task_id}.ps1"
        )

        # PowerShell single-quoted strings are used here so paths
        # containing spaces remain safe.
        #
        # Any single quote in a path is escaped by doubling it.

        def ps_quote(value: Path | str) -> str:
            text = str(value)

            return (
                "'"
                + text.replace("'", "''")
                + "'"
            )

        launcher_script = "\n".join(
            [
                "$ErrorActionPreference = 'Continue'",
                "",
                f"Set-Location -LiteralPath {ps_quote(project_root)}",
                "",
                f"& {ps_quote(python_executable)} "
                f"-m {ps_quote(module)} "
                f"--log {ps_quote(log_path)} "
                f"--task-id {ps_quote(task_id)}",
                "",
                "Write-Host ''",
                "Write-Host '========================================'",
                f"Write-Host 'CASO Worker finished: {task_id}'",
                "Write-Host 'Worker terminal will remain open.'",
                "Write-Host '========================================'",
                "Write-Host ''",
                "Read-Host 'Press ENTER to close this worker tab'",
                "exit",
            ]
        )

        launcher_path.write_text(
            launcher_script,
            encoding="utf-8",
        )

        # ----------------------------------------------------------
        # Launch Windows Terminal.
        #
        # wt.exe now only needs to understand:
        #
        #     powershell.exe -NoExit -File <script>
        #
        # There is no nested -Command string anymore.
        # ----------------------------------------------------------

        command = [
            "wt.exe",
            "new-tab",
            "--title",
            f"CASO Worker | {task_id}",
            "powershell.exe",
            "-NoLogo",
            "-NoExit",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(launcher_path),
        ]

        try:

            subprocess.Popen(
                command,
                creationflags=(
                    subprocess.CREATE_NEW_PROCESS_GROUP
                ),
            )

        except FileNotFoundError:

            print(
                "[CONCURRENT DEBUG] "
                "wt.exe was not found. "
                f"Worker {task_id} will execute normally "
                "without a debug tab.",
                flush=True,
            )

    def open_tabs(
        self,
        *,
        tasks,
    ) -> None:

        for task in tasks:

            self.open_worker_tab(
                task_id=task.task_id,
            )

    def write(
        self,
        *,
        task_id: str,
        event: str,
        message: str = "",
        **metadata,
    ) -> None:

        payload = {
            "timestamp": (datetime.now(timezone.utc).isoformat()),
            "event": event,
            "task_id": task_id,
            "message": message,
            **metadata,
        }

        path = self.log_path(task_id)

        lock = self._locks.setdefault(
            task_id,
            threading.Lock(),
        )

        with lock:

            with path.open(
                "a",
                encoding="utf-8",
            ) as handle:

                handle.write(
                    json.dumps(
                        payload,
                        ensure_ascii=False,
                    )
                    + "\n"
                )

                handle.flush()

    def close_worker(
        self,
        *,
        task_id: str,
        status: str,
        error: str | None = None,
    ) -> None:

        self.write(
            task_id=task_id,
            event="DONE",
            message=(f"Worker completed with status={status}"),
            status=status,
            error=error,
        )
