from agents.terminal.critics.models import (
    CriticDecision,
    CriticDecisionScope,
    CriticOutput,
)


def validate_critic_output(
    critic_output: CriticOutput,
) -> CriticOutput:
    """
    Deterministically validate the semantic contract of a
    CriticOutput.

    This function does not decide whether the Critic's decision
    is correct. It only verifies that the decision can be safely
    passed to the Runtime.
    """

    if not critic_output.rationale.strip():
        raise ValueError(
            "CriticOutput rationale cannot be empty."
        )

    if not critic_output.evidence:
        raise ValueError(
            "CriticOutput must contain at least one "
            "piece of evidence."
        )

    for index, evidence in enumerate(
        critic_output.evidence
    ):
        if not evidence.source.strip():
            raise ValueError(
                f"Critic evidence at index {index} "
                "has an empty source."
            )

        if not evidence.observation.strip():
            raise ValueError(
                f"Critic evidence at index {index} "
                "has an empty observation."
            )

    # ==========================================================
    # Decision / Scope Contract
    # ==========================================================

    decision = critic_output.decision
    scope = critic_output.scope
    targets = critic_output.target_task_ids

    # ----------------------------------------------------------
    # TASK-SCOPED DECISIONS
    # ----------------------------------------------------------
    #
    # These decisions operate on explicitly identified tasks.
    # ----------------------------------------------------------

    task_scoped_decisions = {
        CriticDecision.TASK_COMPLETED,
        CriticDecision.RETRY_TASK,
    }

    # ----------------------------------------------------------
    # PLAN-SCOPED DECISIONS
    # ----------------------------------------------------------
    #
    # CONTINUE_TASK is allowed at PLAN scope for concurrent
    # execution.
    #
    # It means:
    #
    #     continue the rolling plan
    #
    # rather than:
    #
    #     continue one explicitly targeted task.
    # ----------------------------------------------------------

    plan_scoped_decisions = {
        CriticDecision.CONTINUE_TASK,
        CriticDecision.PLAN_UPDATE_REQUIRED,
        CriticDecision.REPLAN_REQUIRED,
    }

    goal_scoped_decisions = {
        CriticDecision.GOAL_COMPLETED,
    }

    # ----------------------------------------------------------
    # Task-scoped decisions
    # ----------------------------------------------------------

    if decision in task_scoped_decisions:

        if scope != CriticDecisionScope.TASK:
            raise ValueError(
                f"Critic decision '{decision.value}' must "
                "use TASK scope."
            )

        if not targets:
            raise ValueError(
                f"Critic decision '{decision.value}' requires "
                "at least one target_task_id."
            )

        for task_id in targets:

            if not task_id.strip():
                raise ValueError(
                    "Critic target_task_ids cannot contain "
                    "empty task IDs."
                )

    # ----------------------------------------------------------
    # Plan-scoped decisions
    # ----------------------------------------------------------

    elif decision in plan_scoped_decisions:

        if scope != CriticDecisionScope.PLAN:
            raise ValueError(
                f"Critic decision '{decision.value}' must "
                "use PLAN scope."
            )

        if targets:
            raise ValueError(
                f"Critic decision '{decision.value}' must not "
                "contain target_task_ids."
            )

    # ----------------------------------------------------------
    # Goal-scoped decisions
    # ----------------------------------------------------------

    elif decision in goal_scoped_decisions:

        if scope != CriticDecisionScope.GOAL:
            raise ValueError(
                f"Critic decision '{decision.value}' must "
                "use GOAL scope."
            )

        if targets:
            raise ValueError(
                f"Critic decision '{decision.value}' must not "
                "contain target_task_ids."
            )
    # ==========================================================
    # GOAL COMPLETION EVIDENCE CONTRACT
    # ==========================================================
    #
    # GOAL_COMPLETED is the terminal semantic decision.
    #
    # The Runtime does not independently understand the Critic's
    # rationale, so require the Critic to explicitly provide
    # concrete completion evidence when making this decision.
    #
    # This does NOT prove the decision is semantically correct.
    # It prevents an unsupported empty/generic GOAL_COMPLETED
    # response from reaching the Runtime.
    # ==========================================================

    if decision == CriticDecision.GOAL_COMPLETED:

        evidence_text = "\n".join(
            (
                f"{item.source}: "
                f"{item.observation}"
            )
            for item in critic_output.evidence
        ).lower()

        rationale = (
            critic_output.rationale
            .strip()
            .lower()
        )

        if len(critic_output.evidence) < 2:
            raise ValueError(
                "GOAL_COMPLETED requires at least two "
                "independent pieces of evidence."
            )

        completion_markers = (
            "completed",
            "created",
            "produced",
            "verified",
            "achieved",
            "satisfied",
            "exists",
            "generated",
            "delivered",
        )

        has_completion_evidence = any(
            marker in evidence_text
            for marker in completion_markers
        )

        if not has_completion_evidence:
            raise ValueError(
                "GOAL_COMPLETED evidence does not contain "
                "an explicit completion observation."
            )

        if (
            "plan completed" in rationale
            and not (
                "goal completed" in rationale
                or "goal achieved" in rationale
                or "goal satisfied" in rationale
            )
        ):
            raise ValueError(
                "GOAL_COMPLETED rationale appears to rely only "
                "on plan completion rather than explicit "
                "overall-goal completion."
            )
            
    return critic_output