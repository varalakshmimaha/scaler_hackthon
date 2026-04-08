"""Task definitions and email datasets for the Email Triage environment."""

from __future__ import annotations

from email_triage_env.models import (
    EmailCategory,
    Department,
    EmailMessage,
    Priority,
    TaskInfo,
)

# ===================================================================
# TASK 1 — Easy: Email Classification
# ===================================================================

TASK1_EMAILS = [
    EmailMessage(
        id="e1",
        sender="deals@superstore-promo.biz",
        subject="YOU WON $1,000,000!!! Click NOW!!!",
        body="Congratulations! You have been selected as our lucky winner. Click the link below to claim your prize immediately. Act now before it expires! http://totallylegit.biz/claim",
        timestamp="2026-04-07T08:12:00Z",
    ),
    EmailMessage(
        id="e2",
        sender="cto@mycompany.com",
        subject="Urgent: Production database is down",
        body="Team, our primary production database went offline at 07:55 UTC. Customer-facing services are impacted. All hands on deck — join the incident bridge immediately. This is a P0.",
        timestamp="2026-04-07T08:00:00Z",
    ),
    EmailMessage(
        id="e3",
        sender="newsletter@techdigest.io",
        subject="This Week in AI — April 7 Edition",
        body="Hello! Here's your weekly roundup of the latest in artificial intelligence. This week: new transformer architectures, open-source model releases, and industry trends. Read more on our blog.",
        timestamp="2026-04-07T07:30:00Z",
    ),
    EmailMessage(
        id="e4",
        sender="jane.doe@facebook.com",
        subject="Jane commented on your post",
        body="Jane Doe commented on your photo: 'Great shot! Where was this taken?' View the comment and reply on Facebook.",
        timestamp="2026-04-07T09:15:00Z",
    ),
    EmailMessage(
        id="e5",
        sender="pm@mycompany.com",
        subject="Q2 sprint planning — please review backlog",
        body="Hi team, please review the backlog items before our sprint planning meeting on Wednesday. I've added new user stories based on customer feedback. Let me know if any items need re-prioritization.",
        timestamp="2026-04-07T10:00:00Z",
    ),
]

TASK1_GROUND_TRUTH = [
    {"email_id": "e1", "category": EmailCategory.SPAM},
    {"email_id": "e2", "category": EmailCategory.IMPORTANT},
    {"email_id": "e3", "category": EmailCategory.NEWSLETTER},
    {"email_id": "e4", "category": EmailCategory.SOCIAL},
    {"email_id": "e5", "category": EmailCategory.WORK},
]

TASK1_INFO = TaskInfo(
    task_id="email_classification",
    task_name="Email Classification",
    difficulty="easy",
    description="Classify each email into one of: spam, important, newsletter, social, work",
    current_step=0,
    total_steps=5,
)

# ===================================================================
# TASK 2 — Medium: Email Prioritization & Routing
# ===================================================================

TASK2_EMAILS = [
    EmailMessage(
        id="e6",
        sender="angry.customer@gmail.com",
        subject="ORDER #9921 STILL NOT DELIVERED — 3 WEEKS LATE",
        body="I placed order #9921 three weeks ago and it still hasn't arrived. I've called twice and nobody can tell me where it is. I want a full refund immediately or I'm filing a chargeback and reporting to the BBB. This is absolutely unacceptable.",
        timestamp="2026-04-07T08:30:00Z",
    ),
    EmailMessage(
        id="e7",
        sender="security@mycompany.com",
        subject="ALERT: Suspicious login detected on admin account",
        body="We detected a login to the admin account from an unrecognized IP address (198.51.100.42) in a country not matching any known employee location. The session is currently active. Immediate action required to verify or revoke access.",
        timestamp="2026-04-07T08:05:00Z",
    ),
    EmailMessage(
        id="e8",
        sender="vendor@officesupplies.com",
        subject="Your monthly supply order confirmation",
        body="This confirms your recurring order for office supplies: 10 boxes of paper, 50 pens, 20 notebooks. Estimated delivery: April 14. No action needed unless you'd like to modify the order.",
        timestamp="2026-04-07T09:00:00Z",
    ),
    EmailMessage(
        id="e9",
        sender="recruiter@mycompany.com",
        subject="New candidate application — Senior Engineer role",
        body="A new application has been submitted for the Senior Engineer position. The candidate has 8 years of experience and strong references. Resume attached. Please review when you have a chance this week.",
        timestamp="2026-04-07T09:30:00Z",
        has_attachment=True,
    ),
    EmailMessage(
        id="e10",
        sender="ceo@mycompany.com",
        subject="Board presentation draft — need review by EOD",
        body="Team, I've attached the draft for tomorrow's board presentation. I need final feedback by end of day today. Focus on the financial projections slide and the product roadmap section. This is time-sensitive.",
        timestamp="2026-04-07T10:00:00Z",
        has_attachment=True,
    ),
]

TASK2_GROUND_TRUTH = [
    {"email_id": "e6", "priority": Priority.HIGH, "department": Department.SUPPORT},
    {"email_id": "e7", "priority": Priority.CRITICAL, "department": Department.ENGINEERING},
    {"email_id": "e8", "priority": Priority.LOW, "department": Department.MARKETING},
    {"email_id": "e9", "priority": Priority.MEDIUM, "department": Department.HR},
    {"email_id": "e10", "priority": Priority.HIGH, "department": Department.MANAGEMENT},
]

TASK2_INFO = TaskInfo(
    task_id="email_prioritization",
    task_name="Email Prioritization & Routing",
    difficulty="medium",
    description="Assign priority (critical/high/medium/low) and route to the correct department (engineering/sales/support/hr/management/marketing)",
    current_step=0,
    total_steps=5,
)

# ===================================================================
# TASK 3 — Hard: Email Response Drafting
# ===================================================================

TASK3_EMAILS = [
    EmailMessage(
        id="e11",
        sender="enterprise.client@bigcorp.com",
        subject="Contract renewal concerns — considering alternatives",
        body="Hi, our contract is up for renewal next month and frankly we've had mixed experiences this year. The outage in February cost us significant revenue, and support response times have been slower than our SLA guarantees. We're evaluating competitors. I'd like to discuss what you can offer to retain our business — both in terms of pricing and service improvements. Can we schedule a call this week?",
        timestamp="2026-04-07T08:00:00Z",
    ),
    EmailMessage(
        id="e12",
        sender="new.hire@mycompany.com",
        subject="Confused about onboarding — several systems not working",
        body="Hi, I started on Monday and I'm having trouble getting set up. My SSO login doesn't work for Jira or Confluence, I haven't received my hardware yet, and I'm not sure who my onboarding buddy is. My manager is on PTO this week. I don't want to fall behind — could someone help me get unblocked? I've tried IT support but the ticket hasn't been picked up yet.",
        timestamp="2026-04-07T09:00:00Z",
    ),
    EmailMessage(
        id="e13",
        sender="regulator@compliance-authority.gov",
        subject="Data handling compliance inquiry — response required within 5 business days",
        body="Dear Data Protection Officer, pursuant to Regulation 14.3(b), we are conducting a routine audit of your organization's data handling practices. Please provide: (1) your current data retention policy, (2) documentation of consent mechanisms for user data collection, (3) records of any data breaches in the past 12 months, and (4) your data processing agreements with third-party vendors. A complete response is required within 5 business days of receipt of this notice.",
        timestamp="2026-04-07T07:00:00Z",
    ),
]

TASK3_GROUND_TRUTH = [
    {
        "email_id": "e11",
        "required_elements": [
            "acknowledge_concerns",
            "apologize_for_outage",
            "offer_meeting",
            "mention_retention_incentive",
            "professional_tone",
        ],
        "forbidden_elements": [
            "blame_customer",
            "dismiss_concerns",
            "make_unrealistic_promises",
        ],
    },
    {
        "email_id": "e12",
        "required_elements": [
            "empathy",
            "actionable_steps",
            "escalation_offer",
            "welcoming_tone",
            "specific_help",
        ],
        "forbidden_elements": [
            "blame_new_hire",
            "dismissive_language",
        ],
    },
    {
        "email_id": "e13",
        "required_elements": [
            "acknowledge_receipt",
            "confirm_timeline",
            "professional_formal_tone",
            "mention_compliance_commitment",
            "outline_next_steps",
        ],
        "forbidden_elements": [
            "casual_tone",
            "refuse_to_comply",
            "provide_actual_data",
        ],
    },
]

TASK3_INFO = TaskInfo(
    task_id="email_response",
    task_name="Email Response Drafting",
    difficulty="hard",
    description="Draft professional, appropriate responses to complex emails. Responses are graded on tone, completeness, and appropriateness.",
    current_step=0,
    total_steps=3,
)

# ===================================================================
# Task registry
# ===================================================================

TASKS = {
    "email_classification": {
        "emails": TASK1_EMAILS,
        "ground_truth": TASK1_GROUND_TRUTH,
        "info": TASK1_INFO,
    },
    "email_prioritization": {
        "emails": TASK2_EMAILS,
        "ground_truth": TASK2_GROUND_TRUTH,
        "info": TASK2_INFO,
    },
    "email_response": {
        "emails": TASK3_EMAILS,
        "ground_truth": TASK3_GROUND_TRUTH,
        "info": TASK3_INFO,
    },
}
