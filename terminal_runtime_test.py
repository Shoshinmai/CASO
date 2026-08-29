from agents.terminal.critics.models import (
    CriticDecision,
    CriticDecisionScope,
    CriticEvidence,
    CriticOutput,
)
from agents.terminal.critics.validator import (
    validate_critic_output,
)


def evidence():
    return [
        CriticEvidence(
            source="test",
            observation="Test evidence.",
        )
    ]


def make_output(
    decision,
    scope,
    target_task_ids=None,
):
    return CriticOutput(
        decision=decision,
        scope=scope,
        target_task_ids=(
            target_task_ids
            if target_task_ids is not None
            else []
        ),
        rationale="Test rationale.",
        evidence=evidence(),
    )


# ==========================================================
# VALID CASES
# ==========================================================

valid_cases = [
    (
        "CONTINUE_TASK",
        make_output(
            CriticDecision.CONTINUE_TASK,
            CriticDecisionScope.TASK,
            ["task-A"],
        ),
    ),

    (
        "TASK_COMPLETED",
        make_output(
            CriticDecision.TASK_COMPLETED,
            CriticDecisionScope.TASK,
            ["task-A"],
        ),
    ),

    (
        "RETRY_TASK",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.TASK,
            ["task-A"],
        ),
    ),

    (
        "RETRY_TASK_MULTIPLE",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.TASK,
            ["task-A", "task-B"],
        ),
    ),

    (
        "PLAN_UPDATE_REQUIRED",
        make_output(
            CriticDecision.PLAN_UPDATE_REQUIRED,
            CriticDecisionScope.PLAN,
            [],
        ),
    ),

    (
        "REPLAN_REQUIRED",
        make_output(
            CriticDecision.REPLAN_REQUIRED,
            CriticDecisionScope.PLAN,
            [],
        ),
    ),

    (
        "GOAL_COMPLETED",
        make_output(
            CriticDecision.GOAL_COMPLETED,
            CriticDecisionScope.GOAL,
            [],
        ),
    ),
]


print("\n========== VALID CASES ==========\n")

for name, output in valid_cases:

    validate_critic_output(output)

    print(
        f"[PASS] {name}"
        f" -> decision={output.decision.value}"
        f", scope={output.scope.value}"
        f", targets={output.target_task_ids}"
    )


# ==========================================================
# INVALID CASES
# ==========================================================

invalid_cases = [
    (
        "RETRY_WITHOUT_TARGET",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.TASK,
            [],
        ),
    ),

    (
        "TASK_COMPLETED_WITHOUT_TARGET",
        make_output(
            CriticDecision.TASK_COMPLETED,
            CriticDecisionScope.TASK,
            [],
        ),
    ),

    (
        "CONTINUE_WITHOUT_TARGET",
        make_output(
            CriticDecision.CONTINUE_TASK,
            CriticDecisionScope.TASK,
            [],
        ),
    ),

    (
        "RETRY_PLAN_SCOPE",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.PLAN,
            [],
        ),
    ),

    (
        "TASK_COMPLETED_PLAN_SCOPE",
        make_output(
            CriticDecision.TASK_COMPLETED,
            CriticDecisionScope.PLAN,
            ["task-A"],
        ),
    ),

    (
        "PLAN_UPDATE_WITH_TARGET",
        make_output(
            CriticDecision.PLAN_UPDATE_REQUIRED,
            CriticDecisionScope.PLAN,
            ["task-A"],
        ),
    ),

    (
        "REPLAN_WITH_TARGET",
        make_output(
            CriticDecision.REPLAN_REQUIRED,
            CriticDecisionScope.PLAN,
            ["task-A"],
        ),
    ),

    (
        "GOAL_COMPLETED_WITH_TARGET",
        make_output(
            CriticDecision.GOAL_COMPLETED,
            CriticDecisionScope.GOAL,
            ["task-A"],
        ),
    ),

    (
        "GOAL_COMPLETED_TASK_SCOPE",
        make_output(
            CriticDecision.GOAL_COMPLETED,
            CriticDecisionScope.TASK,
            ["task-A"],
        ),
    ),

    (
        "PLAN_UPDATE_GOAL_SCOPE",
        make_output(
            CriticDecision.PLAN_UPDATE_REQUIRED,
            CriticDecisionScope.GOAL,
            [],
        ),
    ),

    (
        "EMPTY_TARGET_ID",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.TASK,
            [""],
        ),
    ),

    (
        "WHITESPACE_TARGET_ID",
        make_output(
            CriticDecision.RETRY_TASK,
            CriticDecisionScope.TASK,
            ["   "],
        ),
    ),
]


print("\n========== INVALID CASES ==========\n")

for name, output in invalid_cases:

    try:
        validate_critic_output(output)

    except ValueError as error:
        print(
            f"[PASS] {name}"
            f" -> correctly rejected: {error}"
        )

    else:
        print(
            f"[FAIL] {name}"
            " -> validator accepted invalid output!"
        )


print("\n========== COMPLETE ==========\n")