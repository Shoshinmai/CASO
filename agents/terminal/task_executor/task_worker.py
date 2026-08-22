from __future__ import annotations

import asyncio
from typing import Any

from agents.terminal.prompts.executor_prompt import (
    TERMINAL_EXECUTOR_PROMPT,
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
    - task-local execution result

    The worker does NOT:
    - select tasks
    - mutate the central TaskPlan
    - update task dependencies
    - release newly ready tasks
    - schedule other workers

    Those responsibilities belong to the concurrent
    execution coordinator.
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

        The worker operates on one TaskExecutionContext and returns
        a terminal TaskExecutionResult.

        This method does not mutate the central TaskPlan.
        """

        workflow: ExecutionWorkflow | None = None
        tool_results: list[Any] = []

        try:
            # ==================================================
            # 1. Mark this local execution as running
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
            # 4. Bind workflow to explicitly assigned task
            # ==================================================

            workflow.task_id = task.task_id
            workflow.objective = task.objective

            task_execution.workflow = workflow

            print("\n========== TASK WORKER ==========")
            print(f"TASK ID: {task.task_id}")
            print(f"OBJECTIVE: {task.objective}")

            print("\n========== WORKFLOW ==========")
            print(workflow.model_dump())

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

                # ----------------------------------------------
                # Capture task-local tool result
                # ----------------------------------------------

                tool_result = execution_result.get(
                    "tool_result"
                )

                if tool_result is not None:
                    tool_results.append(
                        tool_result
                    )

                # ----------------------------------------------
                # Update local workflow
                # ----------------------------------------------

                workflow = execution_result[
                    "workflow"
                ]

                task_execution.workflow = workflow

                if execution_result.get("completed"):
                    break

            # ==================================================
            # 6. Determine terminal worker outcome
            # ==================================================

            if workflow.status.value == "completed":

                task_execution.status = (
                    TaskExecutionStatus.COMPLETED
                )

                task_execution.result = {
                    "tool_results": tool_results,
                }

                return TaskExecutionResult(
                    execution_id=task_execution.execution_id,
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=TaskExecutionStatus.COMPLETED,
                    workflow_id=workflow.workflow_id,
                    result=task_execution.result,
                    metadata=task_execution.metadata,
                )

            if workflow.status.value == "cancelled":

                task_execution.status = (
                    TaskExecutionStatus.CANCELLED
                )

                task_execution.result = {
                    "tool_results": tool_results,
                }

                return TaskExecutionResult(
                    execution_id=task_execution.execution_id,
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=TaskExecutionStatus.CANCELLED,
                    workflow_id=workflow.workflow_id,
                    result=task_execution.result,
                    error="Task execution was cancelled.",
                    metadata=task_execution.metadata,
                )

            # --------------------------------------------------
            # Failed workflow
            # --------------------------------------------------

            task_execution.status = (
                TaskExecutionStatus.FAILED
            )

            task_execution.result = {
                "tool_results": tool_results,
            }

            task_execution.error = (
                f"Workflow ended with status: "
                f"{workflow.status.value}"
            )

            return TaskExecutionResult(
                execution_id=task_execution.execution_id,
                plan_id=task_execution.plan_id,
                task_id=task_execution.task_id,
                status=TaskExecutionStatus.FAILED,
                workflow_id=workflow.workflow_id,
                result=task_execution.result,
                error=task_execution.error,
                metadata=task_execution.metadata,
            )

        except asyncio.CancelledError:

            task_execution.status = (
                TaskExecutionStatus.CANCELLED
            )

            task_execution.error = (
                "Task worker was cancelled."
            )

            raise

        except Exception as error:

            task_execution.status = (
                TaskExecutionStatus.FAILED
            )

            task_execution.error = str(error)

            task_execution.result = {
                "tool_results": tool_results,
            }

            return TaskExecutionResult(
                execution_id=task_execution.execution_id,
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
            )