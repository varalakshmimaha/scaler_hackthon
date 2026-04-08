"""Validation script — verifies the environment passes OpenEnv compliance checks."""

from __future__ import annotations

import sys
import traceback

from email_triage_env.env import EmailTriageEnv
from email_triage_env.models import Action, EmailCategory, Priority, Department


def validate():
    env = EmailTriageEnv()
    errors: list[str] = []
    passed: list[str] = []

    # ------------------------------------------------------------------
    # 1. Check reset() returns Observation
    # ------------------------------------------------------------------
    print("[1/6] Testing reset()...")
    try:
        obs = env.reset("email_classification")
        assert obs.emails, "reset() must return non-empty emails"
        assert obs.task_info, "reset() must include task_info"
        assert obs.instructions, "reset() must include instructions"
        passed.append("reset() returns valid Observation")
    except Exception as e:
        errors.append(f"reset() failed: {e}")

    # ------------------------------------------------------------------
    # 2. Check step() returns (obs, reward, done, info)
    # ------------------------------------------------------------------
    print("[2/6] Testing step()...")
    try:
        env.reset("email_classification")
        action = Action(
            action_type="classify",
            email_id="e1",
            category=EmailCategory.SPAM,
        )
        result = env.step(action)
        assert len(result) == 4, "step() must return 4-tuple"
        obs, reward, done, info = result
        assert 0.0 <= reward.score <= 1.0, "reward must be in [0, 1]"
        assert isinstance(done, bool), "done must be bool"
        assert isinstance(info, dict), "info must be dict"
        passed.append("step() returns valid (obs, reward, done, info)")
    except Exception as e:
        errors.append(f"step() failed: {e}")

    # ------------------------------------------------------------------
    # 3. Check state()
    # ------------------------------------------------------------------
    print("[3/6] Testing state()...")
    try:
        env.reset("email_classification")
        state = env.state()
        assert state.task_id == "email_classification"
        assert state.emails
        assert state.done is False
        passed.append("state() returns valid EnvState")
    except Exception as e:
        errors.append(f"state() failed: {e}")

    # ------------------------------------------------------------------
    # 4. Check all three tasks work end-to-end
    # ------------------------------------------------------------------
    print("[4/6] Testing all tasks end-to-end...")

    # Task 1
    try:
        env.reset("email_classification")
        for eid, cat in [("e1", "spam"), ("e2", "important"), ("e3", "newsletter"), ("e4", "social"), ("e5", "work")]:
            action = Action(action_type="classify", email_id=eid, category=EmailCategory(cat))
            obs, reward, done, info = env.step(action)
        assert done is True, "Task 1 should be done after 5 steps"
        assert info.get("final_score", 0) > 0, "Perfect answers should score > 0"
        passed.append("Task 1 (classification) end-to-end OK")
    except Exception as e:
        errors.append(f"Task 1 failed: {e}")

    # Task 2
    try:
        env.reset("email_prioritization")
        actions = [
            ("e6", "high", "support"),
            ("e7", "critical", "engineering"),
            ("e8", "low", "marketing"),
            ("e9", "medium", "hr"),
            ("e10", "high", "management"),
        ]
        for eid, pri, dept in actions:
            action = Action(
                action_type="prioritize", email_id=eid,
                priority=Priority(pri), department=Department(dept),
            )
            obs, reward, done, info = env.step(action)
        assert done is True
        passed.append("Task 2 (prioritization) end-to-end OK")
    except Exception as e:
        errors.append(f"Task 2 failed: {e}")

    # Task 3
    try:
        env.reset("email_response")
        replies = [
            ("e11", "I understand your concerns about the outage and apologize for the disruption. We take this seriously and would like to schedule a call to discuss improved pricing and service commitments for your renewal."),
            ("e12", "Welcome to the team! I'm sorry you're having trouble getting set up. Let me escalate your IT ticket for SSO and Jira access right away, and I'll connect you with your onboarding buddy. We'll get your hardware sorted too."),
            ("e13", "We acknowledge receipt of your compliance inquiry and confirm we will provide all requested documentation within the 5 business day timeline. Our team is committed to full compliance and will gather the data retention policies, consent records, breach logs, and vendor agreements."),
        ]
        for eid, reply in replies:
            action = Action(action_type="draft_reply", email_id=eid, reply_text=reply)
            obs, reward, done, info = env.step(action)
        assert done is True
        passed.append("Task 3 (response) end-to-end OK")
    except Exception as e:
        errors.append(f"Task 3 failed: {e}")

    # ------------------------------------------------------------------
    # 5. Check reward function gives incremental feedback
    # ------------------------------------------------------------------
    print("[5/6] Testing incremental reward feedback...")
    try:
        env.reset("email_classification")
        # Correct action
        a1 = Action(action_type="classify", email_id="e1", category=EmailCategory.SPAM)
        _, r1, _, _ = env.step(a1)
        assert r1.score == 1.0, "Correct answer should score 1.0"
        assert r1.reason, "Reward should include reason"
        assert r1.breakdown, "Reward should include breakdown"

        # Wrong action
        a2 = Action(action_type="classify", email_id="e2", category=EmailCategory.SPAM)
        _, r2, _, _ = env.step(a2)
        assert r2.score == 0.0, "Wrong answer should score 0.0"
        passed.append("Incremental reward feedback works correctly")
    except Exception as e:
        errors.append(f"Reward test failed: {e}")

    # ------------------------------------------------------------------
    # 6. Check trajectory penalties
    # ------------------------------------------------------------------
    print("[6/6] Testing trajectory penalties...")
    try:
        env.reset("email_classification")
        a = Action(action_type="classify", email_id="e1", category=EmailCategory.SPAM)
        env.step(a)
        # Duplicate
        _, r_dup, _, _ = env.step(a)
        assert "duplicate" in r_dup.reason.lower() or "penalty" in r_dup.reason.lower()
        passed.append("Trajectory penalties applied correctly")
    except Exception as e:
        errors.append(f"Penalty test failed: {e}")

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    print("\n" + "=" * 50)
    print("VALIDATION RESULTS")
    print("=" * 50)
    for p in passed:
        print(f"  PASS: {p}")
    for e in errors:
        print(f"  FAIL: {e}")
    print(f"\n  {len(passed)} passed, {len(errors)} failed")

    if errors:
        print("\nValidation FAILED.")
        sys.exit(1)
    else:
        print("\nValidation PASSED — environment is OpenEnv compliant.")
        sys.exit(0)


if __name__ == "__main__":
    validate()
