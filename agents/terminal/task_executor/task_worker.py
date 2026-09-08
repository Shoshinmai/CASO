from __future__ import annotations

import asyncio
from typing import Any

from agents.terminal.memory.execution_manager import (
    ExecutionMemoryManager,
)
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
    - task-local ExecutionMemory lifecycle
    - task-local RuntimeProcessingResult collection

    The worker does NOT:
    - select tasks
    - mutate the central TaskPlan
    - update task dependencies
    - release newly ready tasks
    - schedule other workers
    - mutate central runtime memory
    """

    def __init__(
        self,
        *,
        workflow_runtime: WorkflowRuntime | None = None,
    ) -> None:

        self.workflow_runtime = (
            workflow_runtime if workflow_runtime is not None else WorkflowRuntime()
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

        The task receives one task-local ExecutionMemory attempt.
        Every workflow step is processed through the Runtime
        Processing Pipeline.

        The worker does not mutate central runtime state.
        """

        workflow: ExecutionWorkflow | None = None

        tool_results: list[Any] = []

        processing_results = []

        attempt_id: str | None = None

        try:

            # ==================================================
            # 1. Mark local execution as running
            # ==================================================

            task_execution.status = TaskExecutionStatus.RUNNING

            # ==================================================
            # 2. Build task-local Executor context
            # ==================================================

            execution_context = build_execution_context_for_task(
                state=state,
                task=task,
            )

            prompt = TERMINAL_EXECUTOR_PROMPT.format(**execution_context.model_dump())

            # ==================================================
            # 3. Generate task-local workflow
            # ==================================================

            executor_output: ExecutorOutput = await call_nvidia(
                prompt,
                # "nvidia/nemotron-3.5-lightning-30b-a3b",
                "openai/gpt-oss-20b",
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

            print("\n========== TASK WORKER ==========")

            print(f"TASK ID: {task.task_id}")

            print(f"OBJECTIVE: {task.objective}")

            print("\n========== WORKFLOW ==========")

            print(workflow.model_dump())

            for i, step in enumerate(workflow.steps):

                print(
                    f"\n[STEP-{i + 1}] --> "
                    f"{step.description} : "
                    f"(TOOL -> {step.capability} | "
                    f"ARGS -> {step.arguments} | "
                    f"STATUS -> {step.status})"
                )

            # ==================================================
            # 5. Start task execution-memory attempt
            # ==================================================
            #
            # One TaskWorker execution corresponds to one
            # ExecutionAttempt.
            #
            # The workflow may contain multiple capability steps,
            # but they all belong to this one task execution
            # attempt.
            # ==================================================

            first_step = workflow.steps[0]

            attempt = ExecutionMemoryManager.start_attempt(
                execution_memory=state["execution_memory"],
                capability=first_step.capability,
                strategy=(workflow.execution_strategy),
                arguments=first_step.arguments,
            )

            attempt_id = attempt.attempt_id

            task_execution.active_attempt_id = attempt_id

            print("\n========== EXECUTION MEMORY ==========")

            print(f"TASK ID: {task.task_id}")

            print(f"ATTEMPT ID: {attempt_id}")

            print("STATUS: running")

            # ==================================================
            # 6. Execute workflow until terminal
            # ==================================================

            while workflow.status.value not in (
                "completed",
                "failed",
                "cancelled",
            ):

                execution_result = await self.workflow_runtime.execute_next_step(
                    workflow,
                )

                # --------------------------------------------------
                # Update local workflow.
                # --------------------------------------------------

                workflow = execution_result["workflow"]

                task_execution.workflow = workflow

                # --------------------------------------------------
                # Capture execution-step metadata.
                # --------------------------------------------------

                tool_result = execution_result.get("tool_result")

                step_id = execution_result.get("step_id")

                capability = execution_result.get("capability")

                # --------------------------------------------------
                # Process the actual tool result.
                # --------------------------------------------------

                if tool_result is not None:

                    tool_results.append(tool_result)

                    if not capability:

                        raise ValueError(
                            "WorkflowRuntime returned a tool "
                            "result without the executing "
                            "capability."
                        )

                    processed_result = await process_tool_result(
                        state=state,
                        tool_name=capability,
                        raw_result=tool_result,
                        attempt=(len(processing_results) + 1),
                    )

                    processing_results.append(processed_result)

                    print("\n========== TASK RESULT PROCESSED ==========")

                    print(f"TASK ID: {task.task_id}")

                    print(f"STEP ID: {step_id}")

                    print(f"CAPABILITY: {capability}")

                    print(processed_result)

                if execution_result.get("completed"):
                    break

            # ==================================================
            # 7. Build task-local result payload
            # ==================================================

            task_execution.result = {
                "tool_results": tool_results,
                "processing_results": [
                    result.model_dump() for result in processing_results
                ],
            }

            # ==================================================
            # 8. Finalize ExecutionMemory attempt
            # ==================================================
            #
            # A terminal semantic result is required by
            # ExecutionMemoryManager.finish_attempt().
            #
            # In normal execution, every successful/failed
            # capability invocation produces at least one
            # RuntimeProcessingResult.
            # ==================================================

            if attempt_id is not None:

                final_processing_result = (
                    processing_results[-1] if processing_results else None
                )

                final_execution = (
                    final_processing_result.normalized_result.execution
                    if final_processing_result is not None
                    else None
                )

                ExecutionMemoryManager.finish_attempt(
                    execution_memory=state["execution_memory"],
                    attempt_id=attempt_id,
                    runtime_result=final_processing_result,
                    success=(
                        workflow.status.value == "completed"
                        and (
                            final_execution.success
                            if final_execution is not None
                            else False
                        )
                    ),
                    error=(
                        final_execution.stderr
                        if final_execution is not None
                        else (
                            "Workflow terminated before a "
                            "RuntimeProcessingResult was produced."
                        )
                    ),
                )

                print("\n========== EXECUTION MEMORY ==========")

                print(f"TASK ID: {task.task_id}")

                print(f"ATTEMPT ID: {attempt_id}")

                print(f"PROCESSING RESULTS: {len(processing_results)}")

                print("STATUS: finalized")

                print(
                    f"FINAL ATTEMPT STATUS: "
                    f"{state['execution_memory'].attempts[-1].status.value}"
                )

            completed_attempt = None

            if attempt_id is not None:

                for attempt in state["execution_memory"].attempts:

                    if attempt.attempt_id == attempt_id:
                        completed_attempt = attempt
                        break
            # ==================================================
            # 9. Clear active attempt pointer
            # ==================================================

            task_execution.active_attempt_id = None

            # ==================================================
            # 10. COMPLETED
            # ==================================================

            if workflow.status.value == "completed":

                task_execution.status = TaskExecutionStatus.COMPLETED

                return TaskExecutionResult(
                    execution_id=(task_execution.execution_id),
                    execution_attempt_id=attempt_id,
                    execution_attempt=completed_attempt,
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=(TaskExecutionStatus.COMPLETED),
                    workflow_id=(workflow.workflow_id),
                    result=task_execution.result,
                    metadata=(task_execution.metadata),
                    processing_results=(processing_results),
                )

            # ==================================================
            # 11. CANCELLED
            # ==================================================

            if workflow.status.value == "cancelled":

                task_execution.status = TaskExecutionStatus.CANCELLED

                return TaskExecutionResult(
                    execution_id=(task_execution.execution_id),
                    execution_attempt_id=attempt_id,
                    execution_attempt=completed_attempt,
                    plan_id=task_execution.plan_id,
                    task_id=task_execution.task_id,
                    status=(TaskExecutionStatus.CANCELLED),
                    workflow_id=(workflow.workflow_id),
                    result=task_execution.result,
                    error=("Task execution was cancelled."),
                    metadata=(task_execution.metadata),
                    processing_results=(processing_results),
                )

            # ==================================================
            # 12. FAILED WORKFLOW
            # ==================================================

            task_execution.status = TaskExecutionStatus.FAILED

            task_execution.error = (
                "Workflow ended with status: " f"{workflow.status.value}"
            )

            return TaskExecutionResult(
                execution_id=(task_execution.execution_id),
                execution_attempt_id=attempt_id,
                execution_attempt=completed_attempt,
                plan_id=task_execution.plan_id,
                task_id=task_execution.task_id,
                status=TaskExecutionStatus.FAILED,
                workflow_id=(workflow.workflow_id),
                result=task_execution.result,
                error=(task_execution.error),
                metadata=(task_execution.metadata),
                processing_results=(processing_results),
            )

        # ======================================================
        # Cancellation
        # ======================================================

        except asyncio.CancelledError:

            # --------------------------------------------------
            # If cancellation occurs after the attempt started
            # and we already have a processed result, finalize
            # the attempt as failed/cancelled through the
            # execution-memory lifecycle.
            #
            # We deliberately do not fabricate a
            # RuntimeProcessingResult when none exists.
            # --------------------------------------------------

            if attempt_id is not None:

                try:

                    ExecutionMemoryManager.finish_attempt(
                        execution_memory=state["execution_memory"],
                        attempt_id=attempt_id,
                        runtime_result=(
                            processing_results[-1] if processing_results else None
                        ),
                        success=False,
                        error=str(error),
                    )

                except ValueError:
                    # Do not mask the original worker error.
                    pass

            completed_attempt = None

            if attempt_id is not None:

                for attempt in state["execution_memory"].attempts:

                    if attempt.attempt_id == attempt_id:
                        completed_attempt = attempt
                        break

            task_execution.status = TaskExecutionStatus.CANCELLED

            task_execution.error = "Task worker was cancelled."

            raise

        # ======================================================
        # Unexpected worker failure
        # ======================================================

        except Exception as error:

            # --------------------------------------------------
            # Attempt lifecycle
            # --------------------------------------------------

            if attempt_id is not None and processing_results:

                try:

                    ExecutionMemoryManager.finish_attempt(
                        execution_memory=state["execution_memory"],
                        attempt_id=attempt_id,
                        runtime_result=(processing_results[-1]),
                        success=False,
                        error=str(error),
                    )

                except ValueError:
                    # Do not mask the original worker error.
                    pass

            completed_attempt = None

            if attempt_id is not None and state["execution_memory"].attempts:
                completed_attempt = state["execution_memory"].attempts[-1]

            task_execution.active_attempt_id = None

            task_execution.status = TaskExecutionStatus.FAILED

            task_execution.error = str(error)

            task_execution.result = {
                "tool_results": tool_results,
                "processing_results": [
                    result.model_dump() for result in processing_results
                ],
            }

            return TaskExecutionResult(
                execution_id=(task_execution.execution_id),
                execution_attempt_id=attempt_id,
                execution_attempt=completed_attempt,
                plan_id=task_execution.plan_id,
                task_id=task_execution.task_id,
                status=(TaskExecutionStatus.FAILED),
                workflow_id=(workflow.workflow_id if workflow is not None else None),
                result=(task_execution.result),
                error=str(error),
                metadata=(task_execution.metadata),
                processing_results=(processing_results),
            )
