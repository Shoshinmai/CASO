from __future__ import annotations

import asyncio
from typing import Any

from agents.terminal.prompts.executor_prompt import (
    TERMINAL_EXECUTOR_PROMPT,
)
from agents.terminal.result_processing.processor import (
    process_tool_result,
)
from agents.terminal.runtime.task_execution import (
    TaskExecutionContext,
    TaskExecutionResult,
    TaskExecutionStatus,
)
from agents.terminal.task_executor.context_builder import (
    build_execution_context_for_task,
)
from agents.terminal.task_executor.models import (
    ExecutionWorkflow,
    ExecutorOutput,
)
from agents.terminal.task_executor.workflow_runtime import (
    WorkflowRuntime,
)
from agents.terminal.task_plan.models import (
    TaskItem,
)
from llm.llmclient import call_nvidia


class TaskWorker:
    """
    Task-local execution worker.

    A TaskWorker executes one explicitly assigned TaskItem.

    The worker owns:
    - task-specific execution context
    - workflow generation
    - workflow execution
    - task-local result processing
    - task-local RuntimeProcessingResult collection

    The worker does NOT:
    - select tasks
    - mutate the central TaskPlan
    - update task dependencies
    - release newly ready tasks
    - schedule other workers
    - mutate central runtime memory

    Those responsibilities belong to the concurrent
    execution coordinator/reconciliation layer.
    """

    def __init__(
        self,
        *,
        workflow_runtime: WorkflowRuntime | None = None,
    ) -> None:

        self.workflow_runtime = (
            workflow_runtime
            if workflow_runtime is not None
            else WorkflowRuntime()
        )

    async def execute(
        self,
        *,
        state: dict[str, Any],
        task_execution: TaskExecutionContext,
        task: TaskItem,
    ) -> TaskExecutionResult:
        """
        Execute one explicitly assigned task.

        Every successful tool execution is passed through the
        Runtime Processing Pipeline before the task result is
        returned to the concurrent coordinator.

        Processing remains task-local.

        No central TaskPlan or central runtime memory is mutated.
        """

        workflow: ExecutionWorkflow | None = None

        tool_results: list[Any] = []

        processing_results = []

        try:

            # ==================================================
            # 1. Mark local execution as running
            # ==================================================

            task_execution.status = (
                TaskExecutionStatus.RUNNING
            )

            # ==================================================
            # 2. Build task-local Executor context
            # ==================================================

            execution_context = (
                build_execution_context_for_task(
                    state=state,
                    task=task,
                )
            )

            prompt = TERMINAL_EXECUTOR_PROMPT.format(
                **execution_context.model_dump()
            )

            # ==================================================
            # 3. Generate task-local workflow
            # ==================================================

            executor_output: ExecutorOutput = await call_nvidia(
                prompt,
                "nvidia/nemotron-3.5-lightning-30b-a3b",
                subagent=True,
                state_model=ExecutorOutput,
            )

            workflow = executor_output.workflow

            # ==================================================
            # 4. Bind workflow to assigned task
            # ==================================================

            workflow.task_id = task.task_id
            workflow.objective = task.objective

            task_execution.workflow = workflow

            print(
                "\n========== TASK WORKER =========="
            )

            print(
                f"TASK ID: {task.task_id}"
            )

            print(
                f"OBJECTIVE: {task.objective}"
            )

            print(
                "\n========== WORKFLOW =========="
            )

            print(
                workflow.model_dump()
            )
            for i, step in enumerate(getattr(executor_output.workflow, "steps", [])):
                print(
                    f"\n[STEP-{i+1}] --> {step.description} : (TOOL -> {step.capability} | ARGS -> {step.arguments} | STATUS -> {step.status})"
                )

            # ==================================================
            # 5. Execute workflow until terminal
            # ==================================================

            while workflow.status.value not in (
                "completed",
                "failed",
                "cancelled",
            ):

                execution_result = (
                    await self.workflow_runtime.execute_next_step(
                        workflow,
                    )
                )

                # --------------------------------------------------
                # Update local workflow first.
                # --------------------------------------------------

                workflow = execution_result[
                    "workflow"
                ]

                task_execution.workflow = workflow

                # --------------------------------------------------
                # Capture the exact result metadata supplied
                # by WorkflowRuntime.
                # --------------------------------------------------

                tool_result = execution_result.get(
                    "tool_result"
                )

                step_id = execution_result.get(
                    "step_id"
                )

                capability = execution_result.get(
                    "capability"
                )

                # --------------------------------------------------
                # A terminal state with no tool result can occur
                # when the workflow has already completed.
                # --------------------------------------------------

                if tool_result is not None:

                    tool_results.append(
                        tool_result
                    )

                    if not capability:

                        raise ValueError(
                            "WorkflowRuntime returned a tool result "
                            "without the executing capability."
                        )

                    # ==================================================
                    # 6. Runtime Processing Pipeline
                    # ==================================================
                    #
                    # Process this task's tool result while this
                    # worker still owns an isolated state snapshot.
                    #
                    # The processor:
                    #
                    #   raw result
                    #       ↓
                    #   normalization
                    #       ↓
                    #   artifact decision
                    #       ↓
                    #   observation formatting
                    #       ↓
                    #   memory proposal
                    #
                    # It does NOT mutate central state.
                    # ==================================================

                    processed_result = (
                        await process_tool_result(
                            state=state,
                            tool_name=capability,
                            raw_result=tool_result,
                            attempt=(
                                len(processing_results) + 1
                            ),
                        )
                    )

                    processing_results.append(
                        processed_result
                    )

                    print(
                        "\n========== TASK RESULT PROCESSED =========="
                    )

                    print(
                        f"TASK ID: {task.task_id}"
                    )

                    print(
                        f"STEP ID: {step_id}"
                    )

                    print(
                        f"CAPABILITY: {capability}"
                    )

                    print(
                        processed_result
                    )

                if execution_result.get(
                    "completed"
                ):
                    break

            # ==================================================
            # 7. Build common task-local result payload
            # ==================================================

            task_execution.result = {
                "tool_results": tool_results,
                "processing_results": [
                    result.model_dump()
                    for result in processing_results
                ],
            }

            # ==================================================
            # 8. COMPLETED
            # ==================================================

            if workflow.status.value == "completed":

                task_execution.status = (
                    TaskExecutionStatus.COMPLETED
                )

                return TaskExecutionResult(
                    execution_id=(
                        task_execution.execution_id
                    ),
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=(
                        TaskExecutionStatus.COMPLETED
                    ),
                    workflow_id=workflow.workflow_id,
                    result=task_execution.result,
                    metadata=task_execution.metadata,
                    processing_results=processing_results,
                )

            # ==================================================
            # 9. CANCELLED
            # ==================================================

            if workflow.status.value == "cancelled":

                task_execution.status = (
                    TaskExecutionStatus.CANCELLED
                )

                return TaskExecutionResult(
                    execution_id=(
                        task_execution.execution_id
                    ),
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=(
                        TaskExecutionStatus.CANCELLED
                    ),
                    workflow_id=workflow.workflow_id,
                    result=task_execution.result,
                    error=(
                        "Task execution was cancelled."
                    ),
                    metadata=task_execution.metadata,
                    processing_results=processing_results,
                )

            # ==================================================
            # 10. FAILED WORKFLOW
            # ==================================================

            task_execution.status = (
                TaskExecutionStatus.FAILED
            )

            task_execution.error = (
                "Workflow ended with status: "
                f"{workflow.status.value}"
            )

            return TaskExecutionResult(
                execution_id=(
                    task_execution.execution_id
                ),
                plan_id=task_execution.plan_id,
                task_id=task_execution.task_id,
                status=TaskExecutionStatus.FAILED,
                workflow_id=workflow.workflow_id,
                result=task_execution.result,
                error=task_execution.error,
                metadata=task_execution.metadata,
                processing_results=processing_results,
            )

        # ======================================================
        # Cancellation
        # ======================================================

        except asyncio.CancelledError:

            task_execution.status = (
                TaskExecutionStatus.CANCELLED
            )

            task_execution.error = (
                "Task worker was cancelled."
            )

            raise

        # ======================================================
        # Unexpected worker failure
        # ======================================================

        except Exception as error:

            task_execution.status = (
                TaskExecutionStatus.FAILED
            )

            task_execution.error = str(
                error
            )

            task_execution.result = {
                "tool_results": tool_results,
                "processing_results": [
                    result.model_dump()
                    for result in processing_results
                ],
            }

            return TaskExecutionResult(
                execution_id=(
                    task_execution.execution_id
                ),
                plan_id=task_execution.plan_id,
                task_id=task_execution.task_id,
                status=TaskExecutionStatus.FAILED,
                workflow_id=(
                    workflow.workflow_id
                    if workflow is not None
                    else None
                ),
                result=task_execution.result,
                error=str(error),
                metadata=task_execution.metadata,
                processing_results=processing_results,
            )