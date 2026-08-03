from __future__ import annotations
from datetime import datetime, timezone

from agents.terminal.models import (
    AttemptStatus,
    ExecutionAttempt,
    ExecutionMemory,
    utc_now,
)
from agents.terminal.result_processing.models import RuntimeProcessingResult


class ExecutionMemoryManager:
    """
    Deterministic owner of ExecutionMemory.

    All creation and lifecycle updates of ExecutionAttempt
    records must go through this manager.
    """

    @staticmethod
    def start_attempt(
        *,
        execution_memory: ExecutionMemory,
        capability: str,
        strategy: str,
        arguments: dict,
    ) -> str:
        """
        Create a new execution attempt.

        Returns:
            attempt_id
        """

        attempt = ExecutionAttempt(
            step=len(execution_memory.attempts) + 1,
            capability=capability,
            strategy=strategy,
            arguments=arguments,
            status=AttemptStatus.RUNNING,
        )

        execution_memory.attempts.append(attempt)

        return attempt

    @staticmethod
    def current_attempt(
        execution_memory: ExecutionMemory,
    ) -> ExecutionAttempt | None:
        """
        Return the most recent execution attempt.
        """

        if not execution_memory.attempts:
            return None

        return execution_memory.attempts[-1]

    @staticmethod
    def _find_attempt(
        *,
        execution_memory: ExecutionMemory,
        attempt_id: str,
    ) -> ExecutionAttempt:
        """
        Locate an execution attempt by its identifier.
        """

        for attempt in execution_memory.attempts:
            if attempt.attempt_id == attempt_id:
                return attempt

        raise ValueError(f"Execution attempt '{attempt_id}' not found.")

    @staticmethod
    def finish_attempt(
        *,
        execution_memory: ExecutionMemory,
        attempt_id: str,
        runtime_result: RuntimeProcessingResult,
        success: bool,
        error: str | None = None,
    ) -> None:
        """
        Complete an execution attempt using the processed runtime result.
        """

        print("[FINISH ATTEMPT]")
        print("Attempt ID:", attempt_id)
        
        attempt = ExecutionMemoryManager._find_attempt(
            execution_memory=execution_memory,
            attempt_id=attempt_id,
        )
        print("Before:", attempt.status)

        attempt.status = AttemptStatus.SUCCEEDED if success else AttemptStatus.FAILED

        attempt.completed_at = datetime.now(timezone.utc)

        attempt.outcome = runtime_result.normalized_result.execution

        attempt.progress_made = (
            runtime_result.memory_update.completed_work
            or runtime_result.memory_update.known_facts
            or runtime_result.memory_update.discovered_resources
        )

        attempt.error = error
        print("After:", attempt.status)
    
    @staticmethod
    def add_artifact(
        *,
        execution_memory: ExecutionMemory,
        attempt_id: str,
        artifact_id: str,
    ) -> None:
        """
        Associate an artifact with an execution attempt.

        Args:
            execution_memory: Execution memory to update.
            attempt_id: Identifier of the execution attempt.
            artifact_id: Identifier of the artifact created during the attempt.
        """

        attempt = ExecutionMemoryManager._find_attempt(
            execution_memory=execution_memory,
            attempt_id=attempt_id,
        )

        if artifact_id not in attempt.artifact_ids:
            attempt.artifact_ids.append(artifact_id)
