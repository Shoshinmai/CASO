from __future__ import annotations

from agents.terminal.memory import artifact_store
from agents.terminal.memory.execution_manager import (
    ExecutionMemoryManager,
)
from agents.terminal.models import (
    ArtifactReference,
    MemoryScope,
)
from agents.terminal.result_processing.models import (
    ArtifactAction,
)
from agents.terminal.runtime.task_execution import (
    TaskExecutionResult,
    TaskExecutionStatus,
)
from agents.terminal.task_plan.manager import (
    TaskPlanManager,
)
from agents.terminal.task_plan.models import (
    TaskPlan,
)


class TaskResultReconciler:
    """
    Reconcile terminal task execution results into authoritative
    central runtime state.

    This is the boundary between task-local worker execution and
    central runtime state.

    Workers never mutate:
    - TaskPlan
    - artifact_references
    - central ExecutionMemory

    They return TaskExecutionResult objects containing task-local
    processing results.

    The reconciler centrally applies:
    - task lifecycle results
    - artifact persistence
    - artifact references
    - artifact ↔ execution-attempt associations
    - dependency readiness
    """

    @staticmethod
    def reconcile(
        *,
        plan: TaskPlan,
        results: list[TaskExecutionResult],
        state: dict,
    ) -> TaskPlan:
        """
        Reconcile one completed execution wave.

        The entire result wave is first applied to authoritative
        central state. Dependency readiness is updated only after
        the complete wave has been reconciled.

        Artifact persistence is deterministic and centralized.

        Returns the same mutated TaskPlan instance.
        """

        print(
            f"\n[RECONCILER] "
            f"Starting wave reconciliation | "
            f"plan={plan.plan_id} | "
            f"results={len(results)}"
        )

        print(
            "[RECONCILER] "
            f"Result order: "
            f"{[result.task_id for result in results]}"
        )

        # ------------------------------------------------------
        # Validate that all results belong to this plan.
        # ------------------------------------------------------

        for result in results:

            print(
                f"[RECONCILER] "
                f"Task result | "
                f"task={result.task_id} | "
                f"execution={result.execution_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"status={result.status}"
            )

            if result.plan_id != plan.plan_id:
                raise ValueError(
                    "Cannot reconcile a result belonging to a "
                    f"different plan. Expected '{plan.plan_id}', "
                    f"received '{result.plan_id}'."
                )

        # ------------------------------------------------------
        # Validate central artifact state.
        # ------------------------------------------------------

        artifact_references = state.get(
            "artifact_references"
        )

        if artifact_references is None:
            raise ValueError(
                "Cannot reconcile artifacts because TerminalState "
                "does not contain artifact_references."
            )

        execution_memory = state.get(
            "execution_memory"
        )

        if execution_memory is None:
            raise ValueError(
                "Cannot reconcile artifacts because TerminalState "
                "does not contain execution_memory."
            )

        # ------------------------------------------------------
        # Apply all terminal execution outcomes.
        #
        # Do not update dependency readiness inside this loop.
        # A whole execution wave must be reconciled first.
        # ------------------------------------------------------

        for result in results:

            print(
                f"[RECONCILER] "
                f"Applying task outcome | "
                f"task={result.task_id} | "
                f"status={result.status}"
            )

            if result.status == TaskExecutionStatus.COMPLETED:

                TaskPlanManager.complete_task(
                    plan=plan,
                    task_id=result.task_id,
                )

                continue

            if result.status == TaskExecutionStatus.FAILED:

                TaskPlanManager.fail_task(
                    plan=plan,
                    task_id=result.task_id,
                    reason=(
                        result.error
                        or "Task execution failed."
                    ),
                )

                continue

            if result.status == TaskExecutionStatus.CANCELLED:

                TaskPlanManager.cancel_task(
                    plan=plan,
                    task_id=result.task_id,
                )

                continue

            raise ValueError(
                "Cannot reconcile non-terminal task execution "
                f"status '{result.status}'."
            )

        # ------------------------------------------------------
        # Persist all artifact decisions from the completed wave.
        #
        # This happens centrally AFTER all workers have returned.
        #
        # Workers only produced ArtifactDecision objects.
        # ------------------------------------------------------

        print(
            "[RECONCILER] "
            "Beginning artifact reconciliation."
        )

        for result in results:

            TaskResultReconciler._reconcile_artifacts(
                result=result,
                state=state,
            )

        # ------------------------------------------------------
        # Recompute readiness after the entire wave is applied.
        # ------------------------------------------------------

        print(
            "[RECONCILER] "
            "Updating task readiness."
        )

        TaskPlanManager.update_task_readiness(
            plan=plan,
        )

        # ------------------------------------------------------
        # Mark tasks blocked by failed/cancelled dependencies.
        # ------------------------------------------------------

        blocked_tasks = (
            TaskPlanManager.get_blocked_tasks(
                plan=plan,
            )
        )

        print(
            "[RECONCILER] "
            f"Blocked tasks detected: "
            f"{[task.task_id for task in blocked_tasks]}"
        )

        for task in blocked_tasks:

            TaskPlanManager.block_task(
                plan=plan,
                task_id=task.task_id,
                blocker=(
                    "A required dependency did not complete "
                    "successfully."
                ),
            )

        # ------------------------------------------------------
        # Recompute plan terminal state.
        # ------------------------------------------------------

        if TaskPlanManager.is_plan_complete(
            plan=plan,
        ):
            print(
                "[RECONCILER] "
                "Plan is complete."
            )

            TaskPlanManager.complete_plan(
                plan=plan,
            )

        print(
            f"[RECONCILER] "
            f"Wave reconciliation complete | "
            f"plan={plan.plan_id}"
        )

        return plan

    @staticmethod
    def _reconcile_artifacts(
        *,
        result: TaskExecutionResult,
        state: dict,
    ) -> None:
        """
        Reconcile task-local execution memory and artifacts into
        authoritative central runtime state.

        Ordering is important:

            1. merge the completed execution attempt
            2. persist artifact candidates
            3. associate persisted artifact IDs with that attempt

        This guarantees that concurrent workers never depend on
        completion order or on a global "current attempt".
        """

        artifact_references = state[
            "artifact_references"
        ]

        execution_memory = state[
            "execution_memory"
        ]

        print(
            f"[ARTIFACT] "
            f"Processing task | "
            f"task={result.task_id} | "
            f"attempt={result.execution_attempt_id} | "
            f"processing_results="
            f"{len(result.processing_results)}"
        )

        # ------------------------------------------------------
        # 1. Merge the worker's completed execution attempt.
        # ------------------------------------------------------

        attempt = result.execution_attempt

        if attempt is not None:

            print(
                f"[MEMORY] "
                f"Merging attempt | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id}"
            )

            # Defensive identity check.
            if (
                result.execution_attempt_id is not None
                and attempt.attempt_id
                != result.execution_attempt_id
            ):
                raise ValueError(
                    "TaskExecutionResult execution attempt "
                    "identity mismatch: "
                    f"result has "
                    f"'{result.execution_attempt_id}', "
                    f"but execution_attempt contains "
                    f"'{attempt.attempt_id}'."
                )

            ExecutionMemoryManager.merge_completed_attempt(
                execution_memory=execution_memory,
                attempt=attempt,
            )

            print(
                f"[MEMORY] "
                f"Attempt merged | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id}"
            )

        else:

            print(
                f"[MEMORY] "
                f"No execution attempt payload | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id}"
            )

        # ------------------------------------------------------
        # 2. Persist stored artifact candidates.
        # ------------------------------------------------------

        for processing_result in (
            result.processing_results
        ):

            decision = (
                processing_result.artifact_decision
            )

            print(
                f"[ARTIFACT] "
                f"Decision | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"action={decision.action}"
            )

            if decision.action != ArtifactAction.STORE:

                print(
                    f"[ARTIFACT] "
                    f"Skipping persistence | "
                    f"task={result.task_id} | "
                    f"action={decision.action}"
                )

                continue

            artifact = decision.artifact

            if artifact is None:
                raise ValueError(
                    "Artifact decision requested STORE but "
                    "contained no artifact candidate."
                )

            print(
                f"[ARTIFACT] "
                f"Persisting artifact | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"type={artifact.artifact_type}"
            )

            # --------------------------------------------------
            # Persist artifact globally.
            # --------------------------------------------------

            artifact_id = artifact_store.save(
                artifact_type=artifact.artifact_type,
                summary=artifact.summary,
                data=artifact.data,
                metadata={
                    "plan_id": result.plan_id,
                    "task_id": result.task_id,
                    "execution_id": result.execution_id,
                },
            )

            print(
                f"[ARTIFACT] "
                f"Artifact stored | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"artifact_id={artifact_id}"
            )

            # --------------------------------------------------
            # Create lightweight central reference.
            # --------------------------------------------------

            reference = ArtifactReference(
                artifact_id=artifact_id,
                artifact_type=artifact.artifact_type,
                summary=artifact.summary,
                source=(
                    processing_result
                    .normalized_result
                    .context
                    .tool_name
                ),
                scope=MemoryScope.TASK,
            )

            # --------------------------------------------------
            # Avoid duplicate references.
            # --------------------------------------------------

            already_present = any(
                existing.artifact_id
                == reference.artifact_id
                for existing
                in artifact_references
            )

            if not already_present:

                artifact_references.append(
                    reference
                )

                print(
                    f"[ARTIFACT] "
                    f"Reference registered | "
                    f"task={result.task_id} | "
                    f"artifact_id={artifact_id}"
                )

            else:

                print(
                    f"[ARTIFACT] "
                    f"Reference already present | "
                    f"task={result.task_id} | "
                    f"artifact_id={artifact_id}"
                )

            # --------------------------------------------------
            # 3. Associate artifact with exact attempt.
            # --------------------------------------------------

            print(
                f"[MEMORY] "
                f"Associating artifact | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"artifact={artifact_id}"
            )

            TaskResultReconciler._associate_artifact_with_attempt(
                result=result,
                artifact_id=artifact_id,
                execution_memory=execution_memory,
            )

            print(
                f"[MEMORY] "
                f"Artifact associated | "
                f"task={result.task_id} | "
                f"attempt={result.execution_attempt_id} | "
                f"artifact={artifact_id}"
            )

    @staticmethod
    def _associate_artifact_with_attempt(
        *,
        result: TaskExecutionResult,
        artifact_id: str,
        execution_memory,
    ) -> None:
        """
        Associate an artifact with the exact execution attempt
        that produced the task result.

        Concurrent workers must never rely on
        ExecutionMemoryManager.current_attempt() here because
        multiple workers may complete in arbitrary order.

        The TaskExecutionResult therefore carries the explicit
        execution_attempt_id created by the TaskWorker.
        """

        attempt_id = result.execution_attempt_id

        if not attempt_id:
            raise ValueError(
                "Cannot associate artifact with ExecutionMemory: "
                f"task '{result.task_id}' returned an artifact "
                "without an execution_attempt_id."
            )

        ExecutionMemoryManager.add_artifact(
            execution_memory=execution_memory,
            attempt_id=attempt_id,
            artifact_id=artifact_id,
        )