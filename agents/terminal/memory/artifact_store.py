import uuid

from agents.terminal.memory.artifact import Artifact


class ArtifactStore:

    def __init__(self):

        self._store = {}

    def save(self, artifact_type, summary, data, metadata=None):

        artifact_id = str(uuid.uuid4())

        artifact = Artifact(
            artifact_id=artifact_id,
            artifact_type=artifact_type,
            summary=summary,
            data=data,
            metadata=metadata or {},
        )
        self._store[artifact_id] = artifact

        return artifact_id

    def get(self, artifact_id):

        return self._store.get(artifact_id)

    def get_all(self):

        return list(self._store.values())
