# Email Triage OpenEnv

An [OpenEnv](https://openenv.org)-compliant environment that simulates real-world **email triage** tasks. Agents must classify, prioritize, and draft responses to emails — skills that knowledge workers perform daily.

## Motivation

Email triage is one of the most common real-world tasks performed by professionals. This environment tests an AI agent's ability to:
- **Understand context** — distinguish spam from urgent production alerts
- **Make nuanced judgments** — prioritize and route emails to the right teams
- **Communicate professionally** — draft appropriate replies to sensitive messages

## Tasks

| Task | Difficulty | Description | Emails |
|------|-----------|-------------|--------|
| `email_classification` | Easy | Classify emails as spam, important, newsletter, social, or work | 5 |
| `email_prioritization` | Medium | Assign priority (critical/high/medium/low) and route to a department | 5 |
| `email_response` | Hard | Draft professional replies to complex emails (contract disputes, onboarding issues, compliance inquiries) | 3 |

## Observation Space

Each observation contains:

| Field | Type | Description |
|-------|------|-------------|
| `emails` | `list[EmailMessage]` | Emails to process (id, sender, subject, body, timestamp, has_attachment) |
| `task_info` | `TaskInfo` | Current task metadata (id, name, difficulty, step progress) |
| `instructions` | `str` | What the agent should do |
| `feedback` | `str` | Feedback from the previous action |

## Action Space

| Field | Type | Description |
|-------|------|-------------|
| `action_type` | `str` | One of: `classify`, `prioritize`, `route`, `draft_reply`, `skip` |
| `email_id` | `str` | ID of the email being acted on |
| `category` | `EmailCategory?` | For classification: spam, important, newsletter, social, work |
| `priority` | `Priority?` | For prioritization: critical, high, medium, low |
| `department` | `Department?` | For routing: engineering, sales, support, hr, management, marketing |
| `reply_text` | `str?` | For draft_reply: the response text |

## Reward Function

- **Classification (easy):** 1.0 for correct category, 0.0 for wrong
- **Prioritization (medium):** 50% priority (partial credit for close answers) + 50% department (exact match)
- **Response (hard):** 50% required elements + 30% absence of forbidden elements + 20% length quality
- **Trajectory penalties:** -0.3 for duplicate actions on the same email; skip actions get 0.1

All rewards include `reason` (human-readable explanation) and `breakdown` (per-component scores).

## Setup

### Prerequisites
- Python 3.11+
- Docker (for containerized deployment)

### Local Installation

```bash
pip install -r requirements.txt
```

### Run the Server

```bash
python -m email_triage_env
# Server starts at http://localhost:7860
```

### Run Validation

```bash
python validate.py
```

### Run Baseline Inference

```bash
export HF_TOKEN="hf_your_token_here"
python inference.py --model mistralai/Mixtral-8x7B-Instruct-v0.1
```

### Docker

```bash
docker build -t email-triage-env .
docker run -p 7860:7860 email-triage-env
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Environment info |
| GET | `/tasks` | List available tasks |
| POST | `/reset` | Reset environment (body: `{"task_id": "email_classification"}`) |
| POST | `/step` | Execute an action |
| GET | `/state` | Get current environment state |

## Baseline Performance

| Task | Model | Score |
|------|-------|-------|
| Email Classification (easy) | Mixtral-8x7B-Instruct | ~0.80 |
| Email Prioritization (medium) | Mixtral-8x7B-Instruct | ~0.60 |
| Email Response (hard) | Mixtral-8x7B-Instruct | ~0.55 |
| **Average** | | **~0.65** |

*Scores are approximate and may vary across runs.*

## Project Structure

```
email-triage-env/
├── email_triage_env/
│   ├── __init__.py          # Package exports
│   ├── __main__.py          # Entrypoint
│   ├── models.py            # Pydantic models (Observation, Action, Reward)
│   ├── tasks.py             # Task definitions and email datasets
│   ├── graders.py           # Per-task grading functions
│   ├── env.py               # Core OpenEnv environment
│   └── server.py            # FastAPI HTTP server
├── inference.py             # Baseline inference script
├── validate.py              # OpenEnv compliance validation
├── openenv.yaml             # OpenEnv metadata
├── Dockerfile               # Container definition
├── requirements.txt         # Python dependencies
└── README.md
```

## License

MIT
