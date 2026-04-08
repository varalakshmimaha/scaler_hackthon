"""Pydantic models for the Email Triage OpenEnv environment."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EmailCategory(str, Enum):
    SPAM = "spam"
    IMPORTANT = "important"
    NEWSLETTER = "newsletter"
    SOCIAL = "social"
    WORK = "work"


class Priority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Department(str, Enum):
    ENGINEERING = "engineering"
    SALES = "sales"
    SUPPORT = "support"
    HR = "hr"
    MANAGEMENT = "management"
    MARKETING = "marketing"


# ---------------------------------------------------------------------------
# Core data models
# ---------------------------------------------------------------------------

class EmailMessage(BaseModel):
    """A single email message presented to the agent."""
    id: str
    sender: str
    subject: str
    body: str
    timestamp: str
    has_attachment: bool = False
    reply_to: Optional[str] = None


class TaskInfo(BaseModel):
    """Metadata about the current task."""
    task_id: str
    task_name: str
    difficulty: str
    description: str
    current_step: int = 0
    total_steps: int = 1


# ---------------------------------------------------------------------------
# OpenEnv interface models
# ---------------------------------------------------------------------------

class Observation(BaseModel):
    """What the agent sees at each step."""
    emails: list[EmailMessage] = Field(default_factory=list)
    task_info: TaskInfo
    instructions: str = ""
    feedback: str = ""


class Action(BaseModel):
    """What the agent can do at each step."""
    action_type: str = Field(
        ...,
        description="One of: classify, prioritize, route, draft_reply, skip",
    )
    email_id: str = Field(..., description="ID of the email being acted on")
    category: Optional[EmailCategory] = None
    priority: Optional[Priority] = None
    department: Optional[Department] = None
    reply_text: Optional[str] = None


class Reward(BaseModel):
    """Reward signal returned after each step."""
    score: float = Field(..., ge=0.0, le=1.0)
    reason: str = ""
    breakdown: dict[str, float] = Field(default_factory=dict)


class EnvState(BaseModel):
    """Full internal state of the environment."""
    task_id: str
    emails: list[EmailMessage]
    ground_truth: list[dict]
    current_step: int
    total_steps: int
    done: bool
    cumulative_reward: float
    actions_taken: list[dict]
