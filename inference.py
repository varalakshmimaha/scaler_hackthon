"""Baseline inference script using the OpenAI-compatible API.

Reads HF_TOKEN from environment variables and evaluates a model
against all three email triage tasks.

Usage:
    export HF_TOKEN="hf_..."
    python inference.py [--base-url URL] [--model MODEL]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from openai import OpenAI

from email_triage_env.env import EmailTriageEnv
from email_triage_env.models import Action, EmailCategory, Priority, Department


def build_client(base_url: str, token: str) -> OpenAI:
    return OpenAI(base_url=base_url, api_key=token)


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

def _classification_prompt(emails_json: str) -> str:
    return f"""You are an email triage assistant. Classify each email into exactly one category:
spam, important, newsletter, social, or work.

Emails:
{emails_json}

Respond with a JSON array of objects, each with "email_id" and "category".
Example: [{{"email_id": "e1", "category": "spam"}}]
Return ONLY the JSON array, no extra text."""


def _prioritization_prompt(emails_json: str) -> str:
    return f"""You are an email triage assistant. For each email, assign:
1. A priority: critical, high, medium, or low
2. A department to route to: engineering, sales, support, hr, management, or marketing

Emails:
{emails_json}

Respond with a JSON array of objects, each with "email_id", "priority", and "department".
Example: [{{"email_id": "e6", "priority": "high", "department": "support"}}]
Return ONLY the JSON array, no extra text."""


def _response_prompt(email: dict) -> str:
    return f"""You are a professional email assistant. Draft a reply to this email.
Be professional, empathetic, and address all concerns raised.

From: {email['sender']}
Subject: {email['subject']}
Body: {email['body']}

Write ONLY the reply body text. No subject line, no metadata."""


# ---------------------------------------------------------------------------
# Task runners
# ---------------------------------------------------------------------------

def run_classification(client: OpenAI, model: str, env: EmailTriageEnv) -> float:
    obs = env.reset("email_classification")
    emails_data = [e.model_dump() for e in obs.emails]
    emails_json = json.dumps(emails_data, indent=2)

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _classification_prompt(emails_json)}],
        temperature=0.0,
        max_tokens=500,
    )
    raw = resp.choices[0].message.content.strip()

    try:
        results = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON from the response
        import re
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            results = json.loads(match.group())
        else:
            print(f"  [!] Could not parse model output: {raw[:200]}")
            return 0.0

    total_reward = 0.0
    for item in results:
        try:
            action = Action(
                action_type="classify",
                email_id=item["email_id"],
                category=EmailCategory(item["category"]),
            )
            _, reward, done, info = env.step(action)
            total_reward += reward.score
            print(f"  Email {item['email_id']}: {reward.reason} (score={reward.score})")
        except Exception as exc:
            print(f"  Email {item.get('email_id', '?')}: ERROR — {exc}")

    final = total_reward / 5
    return round(final, 3)


def run_prioritization(client: OpenAI, model: str, env: EmailTriageEnv) -> float:
    obs = env.reset("email_prioritization")
    emails_data = [e.model_dump() for e in obs.emails]
    emails_json = json.dumps(emails_data, indent=2)

    resp = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": _prioritization_prompt(emails_json)}],
        temperature=0.0,
        max_tokens=500,
    )
    raw = resp.choices[0].message.content.strip()

    try:
        results = json.loads(raw)
    except json.JSONDecodeError:
        import re
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            results = json.loads(match.group())
        else:
            print(f"  [!] Could not parse model output: {raw[:200]}")
            return 0.0

    total_reward = 0.0
    for item in results:
        try:
            action = Action(
                action_type="prioritize",
                email_id=item["email_id"],
                priority=Priority(item["priority"]),
                department=Department(item["department"]),
            )
            _, reward, done, info = env.step(action)
            total_reward += reward.score
            print(f"  Email {item['email_id']}: {reward.reason} (score={reward.score})")
        except Exception as exc:
            print(f"  Email {item.get('email_id', '?')}: ERROR — {exc}")

    final = total_reward / 5
    return round(final, 3)


def run_response(client: OpenAI, model: str, env: EmailTriageEnv) -> float:
    obs = env.reset("email_response")
    total_reward = 0.0

    for email in obs.emails:
        email_dict = email.model_dump()
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": _response_prompt(email_dict)}],
            temperature=0.3,
            max_tokens=800,
        )
        reply_text = resp.choices[0].message.content.strip()

        action = Action(
            action_type="draft_reply",
            email_id=email.id,
            reply_text=reply_text,
        )
        _, reward, done, info = env.step(action)
        total_reward += reward.score
        print(f"  Email {email.id}: {reward.reason} (score={reward.score})")

    final = total_reward / 3
    return round(final, 3)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Baseline inference for Email Triage OpenEnv")
    parser.add_argument(
        "--base-url",
        default="https://api-inference.huggingface.co/v1",
        help="OpenAI-compatible API base URL",
    )
    parser.add_argument(
        "--model",
        default="mistralai/Mixtral-8x7B-Instruct-v0.1",
        help="Model name to evaluate",
    )
    args = parser.parse_args()

    token = os.environ.get("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN environment variable is not set.")
        print("Export it with: export HF_TOKEN='hf_...'")
        sys.exit(1)

    client = build_client(args.base_url, token)
    env = EmailTriageEnv()

    print("=" * 60)
    print("Email Triage OpenEnv — Baseline Inference")
    print(f"Model: {args.model}")
    print("=" * 60)

    scores = {}

    print("\n--- Task 1: Email Classification (easy) ---")
    scores["email_classification"] = run_classification(client, args.model, env)
    print(f"  => Score: {scores['email_classification']}")

    print("\n--- Task 2: Email Prioritization (medium) ---")
    scores["email_prioritization"] = run_prioritization(client, args.model, env)
    print(f"  => Score: {scores['email_prioritization']}")

    print("\n--- Task 3: Email Response Drafting (hard) ---")
    scores["email_response"] = run_response(client, args.model, env)
    print(f"  => Score: {scores['email_response']}")

    avg = round(sum(scores.values()) / len(scores), 3)
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    for task_id, score in scores.items():
        print(f"  {task_id:30s} {score:.3f}")
    print(f"  {'AVERAGE':30s} {avg:.3f}")
    print("=" * 60)


if __name__ == "__main__":
    main()
