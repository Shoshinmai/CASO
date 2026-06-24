from agents.terminal.memory import (
    artifact_store
)


class ArtifactRetriever:

    @staticmethod
    def find_file(
        artifact_id: str,
        filename: str
    ):

        artifact = (
            artifact_store.get(
                artifact_id
            )
        )

        if not artifact:
            return []

        matches = []

        for file in artifact.data:

            if (
                filename.lower()
                in file.lower()
            ):
                matches.append(
                    file
                )

        return matches

    @staticmethod
    def count_entries(
        artifact_id: str
    ):

        artifact = (
            artifact_store.get(
                artifact_id
            )
        )

        if not artifact:
            return 0

        return len(
            artifact.data
        )