from __future__ import annotations

import asyncio
import time

from agents.terminal.runtime.concurrent_task_executor import (
    ConcurrentTaskExecutor,
)
from agents.terminal.runtime.task_execution import (
    TaskExecutionResult,
    TaskExecutionStatus,
)
from agents.terminal.runtime.task_runner import (
    AsyncTaskRunner,
)
from agents.terminal.task_plan.models import (
    TaskItem,
)


class FakeTaskRunner(AsyncTaskRunner):
    """
    Deterministic runner used only for concurrency validation.
    """

    def __init__(
        self,
        *,
        delays: dict[str, float],
        failures: set[str] | None = None,
    ) -> None:
        self.delays = delays
        self.failures = failures or set()

    async def execute_task(
        self,
        context,
        *,
        task: TaskItem,
        state: dict,
    ) -> TaskExecutionResult:

        await asyncio.sleep(
            self.delays.get(task.task_id, 0.0)
        )

        if task.task_id in self.failures:
            return TaskExecutionResult(
                execution_id=context.execution_id,
                plan_id=context.plan_id,
                task_id=task.task_id,
                status=TaskExecutionStatus.FAILED,
                error=f"{task.task_id} failed",
            )

        return TaskExecutionResult(
            execution_id=context.execution_id,
            plan_id=context.plan_id,
            task_id=task.task_id,
            status=TaskExecutionStatus.COMPLETED,
        )
        
async def test_independent_tasks_run_concurrently():

    tasks = [
        TaskItem(
            task_id="A",
            objective="Task A",
        ),
        TaskItem(
            task_id="B",
            objective="Task B",
        ),
        TaskItem(
            task_id="C",
            objective="Task C",
        ),
    ]

    runner = FakeTaskRunner(
        delays={
            "A": 1.0,
            "B": 1.0,
            "C": 1.0,
        }
    )

    executor = ConcurrentTaskExecutor(
        runner=runner,
        max_concurrency=3,
    )

    start = time.perf_counter()

    results = await executor.execute(
        plan_id="test-plan",
        tasks=tasks,
        state={},
    )

    elapsed = time.perf_counter() - start

    assert len(results) == 3

    assert all(
        result.status == TaskExecutionStatus.COMPLETED
        for result in results
    )

    # Sequential would be ~3 seconds.
    # Concurrent should be close to ~1 second.
    assert elapsed < 2.0, (
        f"Tasks did not run concurrently. "
        f"Elapsed: {elapsed:.2f}s"
    )

    print(
        f"\nConcurrent execution elapsed: "
        f"{elapsed:.2f}s"
    )
    
async def test_concurrency_limit():

    tasks = [
        TaskItem(task_id="A", objective="A"),
        TaskItem(task_id="B", objective="B"),
        TaskItem(task_id="C", objective="C"),
        TaskItem(task_id="D", objective="D"),
    ]

    runner = FakeTaskRunner(
        delays={
            "A": 1.0,
            "B": 1.0,
            "C": 1.0,
            "D": 1.0,
        }
    )

    executor = ConcurrentTaskExecutor(
        runner=runner,
        max_concurrency=2,
    )

    start = time.perf_counter()

    results = await executor.execute(
        plan_id="test-plan",
        tasks=tasks,
        state={},
    )

    elapsed = time.perf_counter() - start

    assert len(results) == 4

    assert elapsed >= 1.8
    assert elapsed < 3.0

    print(
        f"\nBounded concurrency elapsed: "
        f"{elapsed:.2f}s"
    )
    
async def test_failure_isolation():

    tasks = [
        TaskItem(task_id="A", objective="A"),
        TaskItem(task_id="B", objective="B"),
        TaskItem(task_id="C", objective="C"),
    ]

    runner = FakeTaskRunner(
        delays={
            "A": 0.5,
            "B": 1.0,
            "C": 0.5,
        },
        failures={"B"},
    )

    executor = ConcurrentTaskExecutor(
        runner=runner,
        max_concurrency=3,
    )

    results = await executor.execute(
        plan_id="test-plan",
        tasks=tasks,
        state={},
    )

    status_by_task = {
        result.task_id: result.status
        for result in results
    }

    assert (
        status_by_task["A"]
        == TaskExecutionStatus.COMPLETED
    )

    assert (
        status_by_task["B"]
        == TaskExecutionStatus.FAILED
    )

    assert (
        status_by_task["C"]
        == TaskExecutionStatus.COMPLETED
    )
    
from agents.terminal.runtime.task_result_reconciler import (
    TaskResultReconciler,
)
from agents.terminal.task_plan.manager import (
    TaskPlanManager,
)
from agents.terminal.task_plan.models import (
    TaskItemStatus,
)

def test_wave_reconciliation():

    plan = TaskPlanManager.create_plan(
        goal="dependency test",
        tasks=[
            TaskItem(
                task_id="A",
                objective="A",
                status=TaskItemStatus.READY,
            ),
            TaskItem(
                task_id="B",
                objective="B",
                status=TaskItemStatus.READY,
            ),
            TaskItem(
                task_id="C",
                objective="C",
                dependencies=["A", "B"],
                status=TaskItemStatus.PENDING,
            ),
        ],
    )

    results = [
        TaskExecutionResult(
            execution_id="exec-A",
            plan_id=plan.plan_id,
            task_id="A",
            status=TaskExecutionStatus.COMPLETED,
        ),
        TaskExecutionResult(
            execution_id="exec-B",
            plan_id=plan.plan_id,
            task_id="B",
            status=TaskExecutionStatus.COMPLETED,
        ),
    ]

    # Simulate admission before reconciliation.
    TaskPlanManager.start_task(
        plan=plan,
        task_id="A",
    )

    TaskPlanManager.start_task(
        plan=plan,
        task_id="B",
    )

    TaskResultReconciler.reconcile(
        plan=plan,
        results=results,
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="A",
        ).status
        == TaskItemStatus.COMPLETED
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="B",
        ).status
        == TaskItemStatus.COMPLETED
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="C",
        ).status
        == TaskItemStatus.READY
    )

def test_failed_dependency_blocks_task():

    plan = TaskPlanManager.create_plan(
        goal="failure dependency test",
        tasks=[
            TaskItem(
                task_id="A",
                objective="A",
                status=TaskItemStatus.READY,
            ),
            TaskItem(
                task_id="B",
                objective="B",
                dependencies=["A"],
                status=TaskItemStatus.PENDING,
            ),
            TaskItem(
                task_id="C",
                objective="independent",
                status=TaskItemStatus.READY,
            ),
        ],
    )

    TaskPlanManager.start_task(
        plan=plan,
        task_id="A",
    )

    results = [
        TaskExecutionResult(
            execution_id="exec-A",
            plan_id=plan.plan_id,
            task_id="A",
            status=TaskExecutionStatus.FAILED,
            error="A failed",
        ),
    ]

    TaskResultReconciler.reconcile(
        plan=plan,
        results=results,
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="A",
        ).status
        == TaskItemStatus.FAILED
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="B",
        ).status
        == TaskItemStatus.BLOCKED
    )

    assert (
        TaskPlanManager.get_task(
            plan=plan,
            task_id="C",
        ).status
        == TaskItemStatus.READY
    )

test_failed_dependency_blocks_task()
# test_wave_reconciliation() 

# if __name__ == "__main__":
#     asyncio.run(
#         test_wave_reconciliation()
#     )