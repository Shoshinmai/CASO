from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CASO temporary concurrent worker PowerShell monitor."
    )

    parser.add_argument(
        "--log",
        required=True,
        help="Path to the worker JSONL debug log.",
    )

    parser.add_argument(
        "--task-id",
        required=True,
        help="Task ID displayed by this monitor.",
    )

    parser.add_argument(
        "--poll",
        type=float,
        default=0.10,
        help="Polling interval in seconds.",
    )

    return parser.parse_args()


def format_event(event: dict) -> str:
    event_type = event.get(
        "event",
        "UNKNOWN",
    )

    task_id = event.get(
        "task_id",
        "",
    )

    message = event.get(
        "message",
        "",
    )

    timestamp = event.get(
        "timestamp",
        "",
    )

    if message:
        return (
            f"[{timestamp}] "
            f"{event_type:<12} "
            f"{message}"
        )

    return (
        f"[{timestamp}] "
        f"{event_type:<12} "
        f"task={task_id}"
    )


def main() -> None:
    args = parse_args()

    log_path = Path(
        args.log
    )

    print("=" * 72)
    print(
        f" CASO CONCURRENT WORKER: {args.task_id}"
    )
    print("=" * 72)
    print(
        f"LOG: {log_path}"
    )
    print()

    position = 0

    while True:

        if log_path.exists():

            with log_path.open(
                "r",
                encoding="utf-8",
            ) as handle:

                handle.seek(position)

                while True:

                    line = handle.readline()

                    if not line:
                        break

                    position = handle.tell()

                    line = line.strip()

                    if not line:
                        continue

                    try:
                        event = json.loads(
                            line
                        )

                    except json.JSONDecodeError:
                        print(
                            line,
                            flush=True,
                        )
                        continue

                    print(
                        format_event(event),
                        flush=True,
                    )

                    if event.get(
                        "event"
                    ) == "DONE":

                        print()
                        print(
                            "-" * 72
                        )
                        print(
                            f"Worker {args.task_id} finished."
                        )
                        print(
                            "-" * 72
                        )

                        # Give the user a moment to see
                        # the final event before the tab exits.
                        time.sleep(
                            1.0
                        )

                        return

        time.sleep(
            args.poll
        )


if __name__ == "__main__":
    main()