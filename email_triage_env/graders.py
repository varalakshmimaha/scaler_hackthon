"""Graders for each task — produce a score in [0.0, 1.0]."""

from __future__ import annotations

import re
from email_triage_env.models import Action, Reward


# ---------------------------------------------------------------------------
# Task 1 grader — Email Classification (easy)
# ---------------------------------------------------------------------------

def grade_classification(action: Action, ground_truth: dict) -> Reward:
    """Exact-match grading for email category classification."""
    expected = ground_truth["category"]
    if action.category is None:
        return Reward(
            score=0.0,
            reason="No category provided",
            breakdown={"category_match": 0.0},
        )
    if action.category == expected:
        return Reward(
            score=1.0,
            reason=f"Correct classification: {expected.value}",
            breakdown={"category_match": 1.0},
        )
    return Reward(
        score=0.0,
        reason=f"Wrong classification: got {action.category.value}, expected {expected.value}",
        breakdown={"category_match": 0.0},
    )


# ---------------------------------------------------------------------------
# Task 2 grader — Email Prioritization & Routing (medium)
# ---------------------------------------------------------------------------

_PRIORITY_ORDER = ["critical", "high", "medium", "low"]


def _priority_distance(a: str, b: str) -> int:
    """How many levels apart two priorities are (0 = exact match)."""
    try:
        return abs(_PRIORITY_ORDER.index(a) - _PRIORITY_ORDER.index(b))
    except ValueError:
        return 3  # max distance


def grade_prioritization(action: Action, ground_truth: dict) -> Reward:
    """Grade priority + department routing. 50% weight each."""
    breakdown: dict[str, float] = {}

    # Priority scoring — partial credit for close answers
    if action.priority is None:
        breakdown["priority"] = 0.0
    else:
        dist = _priority_distance(action.priority.value, ground_truth["priority"].value)
        breakdown["priority"] = max(0.0, 1.0 - dist * 0.33)

    # Department scoring — exact match only
    if action.department is None:
        breakdown["department"] = 0.0
    elif action.department == ground_truth["department"]:
        breakdown["department"] = 1.0
    else:
        breakdown["department"] = 0.0

    score = round(0.5 * breakdown["priority"] + 0.5 * breakdown["department"], 3)
    parts = []
    if breakdown["priority"] >= 1.0:
        parts.append("priority correct")
    else:
        parts.append(f"priority partial ({breakdown['priority']:.2f})")
    if breakdown["department"] >= 1.0:
        parts.append("department correct")
    else:
        parts.append("department wrong")

    return Reward(score=score, reason="; ".join(parts), breakdown=breakdown)


# ---------------------------------------------------------------------------
# Task 3 grader — Email Response Drafting (hard)
# ---------------------------------------------------------------------------

_ELEMENT_KEYWORDS: dict[str, list[str]] = {
    # Required positive elements
    "acknowledge_concerns": ["understand", "concern", "hear you", "appreciate", "noted", "recognize"],
    "apologize_for_outage": ["apolog", "sorry", "regret", "unfortunate"],
    "offer_meeting": ["call", "meeting", "schedule", "discuss", "connect", "chat"],
    "mention_retention_incentive": ["discount", "offer", "incentive", "pricing", "value", "renew", "special", "commitment", "improve"],
    "professional_tone": [],  # checked via absence of forbidden markers
    "empathy": ["understand", "frustrating", "sorry", "appreciate", "help", "support"],
    "actionable_steps": ["will", "going to", "next step", "action", "follow up", "reach out", "connect you", "escalate"],
    "escalation_offer": ["escalat", "manager", "senior", "team lead", "personally"],
    "welcoming_tone": ["welcome", "glad", "excited", "happy to help", "great to have"],
    "specific_help": ["sso", "jira", "confluence", "hardware", "laptop", "buddy", "it support", "ticket"],
    "acknowledge_receipt": ["received", "acknowledge", "receipt", "confirm"],
    "confirm_timeline": ["5 business days", "business days", "timeline", "deadline", "by april"],
    "professional_formal_tone": [],  # checked via absence of forbidden markers
    "mention_compliance_commitment": ["compliance", "committed", "priority", "take seriously", "obligation"],
    "outline_next_steps": ["will", "gather", "prepare", "compile", "provide", "send", "coordinate"],
    # Forbidden elements
    "blame_customer": ["your fault", "you should have", "you failed"],
    "dismiss_concerns": ["not a big deal", "overreacting", "don't worry about it"],
    "make_unrealistic_promises": ["guarantee 100%", "will never happen again", "zero downtime forever"],
    "blame_new_hire": ["you should know", "figure it out", "not my problem"],
    "dismissive_language": ["whatever", "not my job", "deal with it"],
    "casual_tone": ["lol", "haha", "no worries dude", "yo ", "sup"],
    "refuse_to_comply": ["refuse", "will not comply", "none of your business"],
    "provide_actual_data": [],  # special: should NOT include real breach data
}


def _element_present(element: str, text: str) -> bool:
    """Check if a required/forbidden element is present in the reply."""
    text_lower = text.lower()
    keywords = _ELEMENT_KEYWORDS.get(element, [])
    if not keywords:
        # For tone-based checks with no keywords, assume present (positive) by default
        return True
    return any(kw in text_lower for kw in keywords)


def grade_response(action: Action, ground_truth: dict) -> Reward:
    """Grade a drafted reply based on required and forbidden elements."""
    if not action.reply_text or len(action.reply_text.strip()) < 20:
        return Reward(
            score=0.0,
            reason="Reply is missing or too short (min 20 chars)",
            breakdown={"length": 0.0},
        )

    reply = action.reply_text
    required = ground_truth.get("required_elements", [])
    forbidden = ground_truth.get("forbidden_elements", [])

    breakdown: dict[str, float] = {}

    # Required elements — each contributes equally
    req_hits = 0
    for elem in required:
        hit = _element_present(elem, reply)
        breakdown[f"req_{elem}"] = 1.0 if hit else 0.0
        if hit:
            req_hits += 1
    req_score = req_hits / max(len(required), 1)

    # Forbidden elements — any hit is a penalty
    penalties = 0
    for elem in forbidden:
        hit = _element_present(elem, reply)
        breakdown[f"forbid_{elem}"] = 0.0 if hit else 1.0
        if hit:
            penalties += 1
    penalty_score = 1.0 - (penalties / max(len(forbidden), 1))

    # Length quality bonus — reward substantive but not excessively long replies
    word_count = len(reply.split())
    if word_count < 30:
        length_score = 0.5
    elif word_count > 500:
        length_score = 0.7
    else:
        length_score = 1.0
    breakdown["length_quality"] = length_score

    score = round(0.5 * req_score + 0.3 * penalty_score + 0.2 * length_score, 3)

    return Reward(
        score=score,
        reason=f"Required: {req_hits}/{len(required)}, Penalties: {penalties}/{len(forbidden)}, Length: {word_count}w",
        breakdown=breakdown,
    )


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

GRADERS = {
    "email_classification": grade_classification,
    "email_prioritization": grade_prioritization,
    "email_response": grade_response,
}
