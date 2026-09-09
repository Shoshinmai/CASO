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

        python_executable = sys.executable

        module = "agents.terminal.runtime.debug_worker_tab"

        # ----------------------------------------------------------
        # Build a PowerShell command.
        #
        # PowerShell stays alive after the Python monitor exits.
        # The monitor itself waits for ENTER after DONE, so the
        # debugging window remains available for inspection.
        # ----------------------------------------------------------

        python_command = (
            f'& "{python_executable}" '
            f'-m "{module}" '
            f'--log "{log_path}" '
            f'--task-id "{task_id}"'
        )

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
            "-Command",
            python_command,
        ]

        try:

            subprocess.Popen(
                command,
                creationflags=(subprocess.CREATE_NEW_PROCESS_GROUP),
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
