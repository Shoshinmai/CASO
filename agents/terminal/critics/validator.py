from agents.terminal.critics.models import (
    CriticDecision,
    CriticDecisionScope,
    CriticOutput,
)


def validate_critic_output(
    critic_output: CriticOutput,
) -> CriticOutput:
    """
    Deterministically validate the structural contract of a
    CriticOutput.

    This function does not decide whether the Critic's semantic
    decision is correct.

    In particular, evidence sufficiency is NOT measured by a fixed
    evidence count. A single authoritative observation may be
    sufficient for a small, self-contained objective.
    """

    # ==========================================================
    # Basic output contract
    # ==========================================================

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

    task_scoped_decisions = {
        CriticDecision.TASK_COMPLETED,
        CriticDecision.RETRY_TASK,
    }

    # ----------------------------------------------------------
    # PLAN-SCOPED DECISIONS
    # ----------------------------------------------------------

    plan_scoped_decisions = {
        CriticDecision.CONTINUE_TASK,
        CriticDecision.PLAN_UPDATE_REQUIRED,
        CriticDecision.REPLAN_REQUIRED,
    }

    # ----------------------------------------------------------
    # GOAL-SCOPED DECISIONS
    # ----------------------------------------------------------

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
    # GOAL_COMPLETED remains a semantic decision owned by the
    # Critic.
    #
    # The validator does NOT attempt to independently determine
    # whether the user's goal is complete.
    #
    # It only ensures that:
    #
    #   1. evidence exists,
    #   2. the Critic's evidence contains a concrete observation
    #      related to completion,
    #   3. the Critic does not explicitly justify completion only
    #      from TaskPlan exhaustion.
    #
    # There is intentionally NO fixed evidence-count requirement.
    #
    # A single authoritative result can be sufficient:
    #
    #   "Determine current working directory"
    #
    #   run_terminal -> D:\AI_dev\CASO
    #
    # Conversely, a complex investigation may require several
    # observations. That determination belongs to the Critic.
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

        # ------------------------------------------------------
        # Completion evidence must say something meaningful
        # about completion.
        #
        # We intentionally do NOT require multiple pieces of
        # evidence. One authoritative observation is valid.
        # ------------------------------------------------------

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
            "identified",
            "determined",
            "confirmed",
            "found",
        )

        has_completion_evidence = any(
            marker in evidence_text
            for marker in completion_markers
        )

        if not has_completion_evidence:
            raise ValueError(
                "GOAL_COMPLETED evidence does not contain "
                "an explicit observation supporting completion."
            )

        # ------------------------------------------------------
        # Prevent the Critic from using plan exhaustion itself
        # as the semantic proof of goal completion.
        #
        # This still allows a plan-exhausted review to conclude
        # GOAL_COMPLETED when the evidence actually establishes
        # the goal.
        # ------------------------------------------------------

        plan_completion_markers = (
            "plan completed",
            "all planned tasks completed",
            "plan exhausted",
            "no tasks remain",
            "all tasks completed",
        )

        has_plan_completion_signal = any(
            marker in evidence_text
            for marker in plan_completion_markers
        )

        explicit_goal_markers = (
            "goal completed",
            "goal achieved",
            "goal satisfied",
            "request satisfied",
            "overall goal",
            "user goal",
            "required result",
            "required deliverable",
        )

        has_explicit_goal_signal = any(
            marker in evidence_text
            or marker in rationale
            for marker in explicit_goal_markers
        )

        if (
            has_plan_completion_signal
            and not has_explicit_goal_signal
            and not has_completion_evidence
        ):
            raise ValueError(
                "GOAL_COMPLETED cannot be justified solely by "
                "TaskPlan completion or exhaustion."
            )

    return critic_output