from agents.terminal.memory import artifact_store


def is_file_listing(command):

    command = command.lower()

    return "dir" in command and ".py" in command


def observation_manager_node(state):

    output = state["raw_observation"]

    command = state["command"]

    if is_file_listing(command):

        files = [line.strip() for line in output.splitlines() if line.strip()]

        summary = f"Found {len(files)} " f"Python files."

        artifact_id = artifact_store.save(
            artifact_type="file_listing",
            summary=summary,
            data=files,
            metadata={"count": len(files)},
        )
        print(f"\n[ARTIFACT CREATED] " f"{artifact_id}")
        print(f"[FILES STORED] " f"{len(files)}")
        existing = state.get("artifact_ids", [])
        print("\n[ARTIFACT IDS BEFORE]")
        print(existing)
        updated = existing + [artifact_id]

        print("\n[ARTIFACT IDS AFTER]")
        print(updated)
        return {
            "compressed_observation": summary,
            "artifact_ids": updated,
        }

    return {"compressed_observation": output}
