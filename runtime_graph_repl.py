import asyncio
import uuid

from agents.terminal.runtime_graph import runtime_graph


def build_initial_state(
    goal: str,
) -> dict:
    return {
        "goal": goal,
    }


async def run_terminal_repl() -> None:
    thread_id = f"terminal-repl-{uuid.uuid4()}"

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    print("=" * 70)
    print("CASO TERMINAL AGENT — INTERACTIVE SESSION")
    print("=" * 70)
    print(f"thread_id: {thread_id}")
    print("Type 'quit', 'exit', or ':q' to terminate.")
    print()

    while True:
        try:
            goal = input("You > ").strip()

        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            break

        if not goal:
            continue

        if goal.lower() in {
            "quit",
            "exit",
            ":q",
        }:
            print("Exiting...")
            break

        print("\n[RUNNING]\n")

        try:
            result = await runtime_graph.ainvoke(
                build_initial_state(goal),
                config,
            )

        except Exception as exc:
            print("\n[ERROR]")
            print(exc)
            print()
            continue

        print("\n[RESULT]")
        print(result)
        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(
        run_terminal_repl()
    )