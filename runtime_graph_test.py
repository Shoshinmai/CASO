import pytest
from agents.terminal.critics.integration import build_critic_runtime_event
from agents.terminal.critics.models import CriticOutput
from agents.terminal.nodes.tool_compiler import compile_execution_step
from agents.terminal.runtime_graph import executor_stage_router, runtime_graph
from agents.terminal.task_executor.models import ExecutionStep
from agents.terminal.task_plan.manager import TaskPlanManager
from agents.terminal.task_plan.models import TaskItem, TaskItemStatus


def test_runtime_graph_contains_required_nodes():

    nodes = set(
        runtime_graph.get_graph().nodes.keys()
    )

    expected = {
        "task_initializer",
        "runtime_initialization",
        "planner",
        "planner_runtime",
        "executor_stage",
        "executor",
        "workflow_execution",
        "message_adapter",
        "runtime_memory_update",
        "critic",
        "critic_runtime",
    }

    missing = expected - nodes

    assert not missing, (
        f"Runtime graph is missing nodes: {missing}"
    )
    
def test_runtime_graph_has_no_legacy_nodes():

    nodes = set(
        runtime_graph.get_graph().nodes.keys()
    )

    legacy = {
        "observer",
        "evaluator",
        "validator",
        "safety_filter",
        "artifact_retriever",
        "observation_manager",
    }

    unexpected = nodes & legacy

    assert not unexpected, (
        f"Legacy nodes are still registered: {unexpected}"
    )
    
def test_executor_stage_routes_to_executor_when_no_workflow():

    state = {
        "execution_workflow": None,
    }

    assert (
        executor_stage_router(state)
        == "executor"
    )
    
def test_executor_stage_routes_to_workflow_execution():

    state = {
        "execution_workflow": object(),
    }

    assert (
        executor_stage_router(state)
        == "workflow_execution"
    )
    
def test_executor_stage_routes_to_workflow_execution():

    state = {
        "execution_workflow": object(),
    }

    assert (
        executor_stage_router(state)
        == "workflow_execution"
    )
    
def test_workflow_execution_chain():

    graph = runtime_graph.get_graph()

    edges = graph.edges

    assert any(
        edge.source == "workflow_execution"
        and edge.target == "message_adapter"
        for edge in edges
    )

    assert any(
        edge.source == "message_adapter"
        and edge.target == "runtime_memory_update"
        for edge in edges
    )
    
def test_workflow_execution_chain():

    graph = runtime_graph.get_graph()

    edges = graph.edges

    assert any(
        edge.source == "workflow_execution"
        and edge.target == "message_adapter"
        for edge in edges
    )

    assert any(
        edge.source == "message_adapter"
        and edge.target == "runtime_memory_update"
        for edge in edges
    )
    
def test_runtime_stage_targets():

    graph = runtime_graph.get_graph()

    nodes = set(
        graph.nodes.keys()
    )

    assert "planner" in nodes
    assert "executor_stage" in nodes
    assert "critic" in nodes
    
def test_executor_stage_has_both_execution_paths():

    graph = runtime_graph.get_graph()

    edges = graph.edges

    assert any(
        edge.source == "executor_stage"
        and edge.target == "executor"
        for edge in edges
    )

    assert any(
        edge.source == "executor_stage"
        and edge.target == "workflow_execution"
        for edge in edges
    )


def test_critic_chain():

    graph = runtime_graph.get_graph()

    edges = graph.edges

    assert any(
        edge.source == "critic"
        and edge.target == "critic_runtime"
        for edge in edges
    )
    
def test_runtime_consistency_node_exists():

    nodes = set(
        runtime_graph.get_graph().nodes.keys()
    )

    assert "runtime_consistency" in nodes
    
def test_execution_result_routes_through_consistency():

    graph = runtime_graph.get_graph()

    assert any(
        edge.source == "runtime_memory_update"
        and edge.target == "runtime_consistency"
        for edge in graph.edges
    )
    
def test_consistency_routes_back_to_runtime_stage():

    graph = runtime_graph.get_graph()

    targets = {
        edge.target
        for edge in graph.edges
        if edge.source == "runtime_consistency"
    }

    assert "planner" in targets
    assert "executor_stage" in targets
    assert "critic" in targets
    
def test_update_remaining_tasks_removes_in_progress_task():

    completed = TaskItem(
        task_id="task-1",
        objective="Completed objective",
        status=TaskItemStatus.COMPLETED,
    )

    current = TaskItem(
        task_id="task-2",
        objective="Old current objective",
        status=TaskItemStatus.IN_PROGRESS,
    )

    replacement = TaskItem(
        task_id="task-3",
        objective="New objective",
        status=TaskItemStatus.IN_PROGRESS,  # deliberately invalid input
    )

    plan = TaskPlanManager.create_plan(
        goal="test",
        tasks=[completed, current],
    )

    TaskPlanManager.update_remaining_tasks(
        plan=plan,
        tasks=[replacement],
    )

    assert len(plan.tasks) == 2

    assert plan.tasks[0].task_id == "task-1"
    assert plan.tasks[0].status == TaskItemStatus.COMPLETED

    assert plan.tasks[1].task_id == "task-3"
    assert plan.tasks[1].status == TaskItemStatus.READY
    
def test_completed_task_cannot_be_started():

    task = TaskItem(
        task_id="task-1",
        objective="Already completed",
        status=TaskItemStatus.COMPLETED,
    )

    plan = TaskPlanManager.create_plan(
        goal="test",
        tasks=[task],
    )

    with pytest.raises(ValueError):
        TaskPlanManager.start_task(
            plan=plan,
            task_id="task-1",
        )
        
def test_ready_task_can_start():

    task = TaskItem(
        task_id="task-1",
        objective="Do something",
        status=TaskItemStatus.READY,
    )

    plan = TaskPlanManager.create_plan(
        goal="test",
        tasks=[task],
    )

    TaskPlanManager.start_task(
        plan=plan,
        task_id="task-1",
    )

    assert plan.tasks[0].status == TaskItemStatus.IN_PROGRESS
    
def test_only_in_progress_task_can_complete():

    task = TaskItem(
        task_id="task-1",
        objective="Do something",
        status=TaskItemStatus.READY,
    )

    plan = TaskPlanManager.create_plan(
        goal="test",
        tasks=[task],
    )

    with pytest.raises(ValueError):
        TaskPlanManager.complete_task(
            plan=plan,
            task_id="task-1",
        )
        
def test_compile_execution_step_rejects_unresolved_reference():

    step = ExecutionStep(
        step_id="step-1",
        description="Run located script",
        capability="run_terminal",
        arguments={
            "command": (
                "python ${search_files.result[0].path}"
            )
        },
    )

    with pytest.raises(ValueError, match="unresolved workflow"):
        compile_execution_step(step)
        
def test_compile_execution_step_rejects_nested_reference():

    step = ExecutionStep(
        step_id="step-1",
        description="Run command",
        capability="run_terminal",
        arguments={
            "command": {
                "value": "{previous.result}"
            }
        },
    )

    with pytest.raises(ValueError, match="unresolved workflow"):
        compile_execution_step(step)
        
