"""Core OpenEnv environment implementation."""

from __future__ import annotations

import copy
from typing import Any

from email_triage_env.graders import GRADERS
from email_triage_env.models import Action, EnvState, Observation, Reward, TaskInfo
from email_triage_env.tasks import TASKS


class EmailTriageEnv:
    """OpenEnv-compliant Email Triage environment.

    Implements:
        step(action)  -> (observation, reward, done, info)
        reset(task_id) -> observation
        state()       -> current internal state
    """

    def __init__(self) -> None:
        self._task_id: str = ""
        self._emails: list = []
        self._ground_truth: list[dict] = []
        self._task_info: TaskInfo | None = None
        self._current_step: int = 0
        self._total_steps: int = 0
        self._done: bool = True
        self._cumulative_reward: float = 0.0
        self._actions_taken: list[dict] = []

    # ------------------------------------------------------------------
    # OpenEnv interface
    # ------------------------------------------------------------------

    def reset(self, task_id: str = "email_classification") -> Observation:
        """Reset the environment to the beginning of a task."""
        if task_id not in TASKS:
            raise ValueError(
                f"Unknown task '{task_id}'. Available: {list(TASKS.keys())}"
            )
        task = TASKS[task_id]
        self._task_id = task_id
        self._emails = copy.deepcopy(task["emails"])
        self._ground_truth = copy.deepcopy(
            [gt if isinstance(gt, dict) else gt.model_dump() for gt in task["ground_truth"]]
        )
        self._task_info = task["info"].model_copy(deep=True)
        self._task_info.current_step = 0
        self._current_step = 0
        self._total_steps = self._task_info.total_steps
        self._done = False
        self._cumulative_reward = 0.0
        self._actions_taken = []

        return self._make_observation(
            feedback="Task started. Process each email according to the instructions."
        )

    def step(self, action: Action) -> tuple[Observation, Reward, bool, dict[str, Any]]:
        """Execute one action and return (observation, reward, done, info)."""
        if self._done:
            raise RuntimeError("Episode is done. Call reset() first.")

        # Validate email_id
        gt = self._ground_truth_for(action.email_id)
        if gt is None:
            reward = Reward(score=0.0, reason=f"Unknown email_id: {action.email_id}")
        else:
            grader = GRADERS[self._task_id]
            reward = grader(action, gt)

        # Penalize destructive / loop actions
        reward = self._apply_trajectory_penalties(action, reward)

        self._cumulative_reward += reward.score
        self._actions_taken.append(action.model_dump())
        self._current_step += 1
        if self._task_info:
            self._task_info.current_step = self._current_step

        self._done = self._current_step >= self._total_steps

        info: dict[str, Any] = {
            "cumulative_reward": round(self._cumulative_reward, 3),
            "steps_remaining": max(0, self._total_steps - self._current_step),
        }
        if self._done:
            info["final_score"] = round(
                self._cumulative_reward / max(self._total_steps, 1), 3
            )

        obs = self._make_observation(feedback=reward.reason)
        return obs, reward, self._done, info

    def state(self) -> EnvState:
        """Return the full internal state of the environment."""
        return EnvState(
            task_id=self._task_id,
            emails=[e.model_copy(deep=True) for e in self._emails],
            ground_truth=copy.deepcopy(self._ground_truth),
            current_step=self._current_step,
            total_steps=self._total_steps,
            done=self._done,
            cumulative_reward=round(self._cumulative_reward, 3),
            actions_taken=copy.deepcopy(self._actions_taken),
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_observation(self, feedback: str = "") -> Observation:
        if self._task_info is None:
            raise RuntimeError("No task loaded — call reset() first.")

        instructions = self._get_instructions()
        return Observation(
            emails=[e.model_copy(deep=True) for e in self._emails],
            task_info=self._task_info.model_copy(deep=True),
            instructions=instructions,
            feedback=feedback,
        )

    def _get_instructions(self) -> str:
        if self._task_id == "email_classification":
            return (
                "Classify each email into exactly one category: "
                "spam, important, newsletter, social, or work. "
                "Use action_type='classify' and set the 'category' field."
            )
        if self._task_id == "email_prioritization":
            return (
                "For each email, assign a priority (critical/high/medium/low) "
                "and route it to a department (engineering/sales/support/hr/management/marketing). "
                "Use action_type='prioritize' and set both 'priority' and 'department' fields."
            )
        return (
            "Draft a professional reply to each email. "
            "Use action_type='draft_reply' and put your response in the 'reply_text' field. "
            "Replies should be appropriate in tone, address all concerns, and propose next steps."
        )

    def _ground_truth_for(self, email_id: str) -> dict | None:
        for gt in self._ground_truth:
            if gt.get("email_id") == email_id:
                return gt
        return None

    def _apply_trajectory_penalties(self, action: Action, reward: Reward) -> Reward:
        """Penalize repeated / destructive actions."""
        # Duplicate action on same email
        seen_ids = [a.get("email_id") for a in self._actions_taken]
        if action.email_id in seen_ids:
            new_score = max(0.0, reward.score - 0.3)
            return Reward(
                score=round(new_score, 3),
                reason=reward.reason + " [PENALTY: duplicate action on same email]",
                breakdown={**reward.breakdown, "duplicate_penalty": -0.3},
            )
        # Skip action
        if action.action_type == "skip":
            return Reward(
                score=0.1,
                reason="Skipped — minimal credit",
                breakdown={"skip": 0.1},
            )
        return reward
