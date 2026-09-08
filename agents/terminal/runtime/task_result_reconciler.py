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

        # ------------------------------------------------------
        # Validate that all results belong to this plan.
        # ------------------------------------------------------

        for result in results:

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

        for result in results:

            TaskResultReconciler._reconcile_artifacts(
                result=result,
                state=state,
            )

        # ------------------------------------------------------
        # Recompute readiness after the entire wave is applied.
        # ------------------------------------------------------

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
            TaskPlanManager.complete_plan(
                plan=plan,
            )

        return plan

    @staticmethod
    def _reconcile_artifacts(
        *,
        result: TaskExecutionResult,
        state: dict,
    ) -> None:
        """
        Persist stored artifact candidates produced by one task.

        Each RuntimeProcessingResult corresponds to one workflow
        capability execution.

        Only ArtifactDecision(action=STORE) results are persisted.

        The resulting artifact is represented centrally by a
        lightweight ArtifactReference.

        Artifact persistence is idempotent within this result
        reconciliation pass because the resulting reference is
        checked before insertion.
        """

        artifact_references = state[
            "artifact_references"
        ]

        execution_memory = state[
            "execution_memory"
        ]

        for processing_result in (
            result.processing_results
        ):

            decision = (
                processing_result.artifact_decision
            )

            if decision.action != ArtifactAction.STORE:
                continue

            artifact = decision.artifact

            if artifact is None:
                raise ValueError(
                    "Artifact decision requested STORE but "
                    "contained no artifact candidate."
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

            # --------------------------------------------------
            # Associate artifact with the execution attempt.
            #
            # D.7.2 worker execution memory is task-local.
            # The TaskExecutionResult must therefore expose
            # enough information for us to identify that attempt.
            # --------------------------------------------------

            TaskResultReconciler._associate_artifact_with_attempt(
                result=result,
                artifact_id=artifact_id,
                execution_memory=execution_memory,
            )

    @staticmethod
    def _associate_artifact_with_attempt(
        *,
        result: TaskExecutionResult,
        artifact_id: str,
        execution_memory,
    ) -> None:
        """
        Associate an artifact with the execution attempt that
        produced the task result.

        D.7.2 keeps ExecutionMemory task-local, so the exact
        attempt association is only possible when the worker
        exposes its attempt identity in the returned result
        metadata.

        The current D.7.2 TaskExecutionResult does not yet carry
        that attempt ID explicitly.

        Therefore this helper intentionally performs no guessed
        association. D.7.4 will add the explicit result-bound
        execution-attempt identity before wiring this association.
        """

        return