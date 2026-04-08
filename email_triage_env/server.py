"""FastAPI server exposing the Email Triage environment as an HTTP API."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from email_triage_env.env import EmailTriageEnv
from email_triage_env.models import Action, Observation, Reward, EnvState
from email_triage_env.tasks import TASKS

app = FastAPI(
    title="Email Triage OpenEnv",
    description="An OpenEnv environment for real-world email triage tasks",
    version="1.0.0",
)

# Single global environment instance
env = EmailTriageEnv()


class ResetRequest(BaseModel):
    task_id: str = "email_classification"


class StepResponse(BaseModel):
    observation: Observation
    reward: Reward
    done: bool
    info: dict


@app.get("/")
def root():
    return {
        "name": "email-triage-env",
        "version": "1.0.0",
        "tasks": list(TASKS.keys()),
        "status": "ready",
    }


@app.get("/tasks")
def list_tasks():
    return {
        tid: {
            "name": t["info"].task_name,
            "difficulty": t["info"].difficulty,
            "description": t["info"].description,
            "num_emails": len(t["emails"]),
        }
        for tid, t in TASKS.items()
    }


@app.post("/reset", response_model=Observation)
def reset(req: ResetRequest):
    try:
        obs = env.reset(task_id=req.task_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return obs


@app.post("/step", response_model=StepResponse)
def step(action: Action):
    try:
        obs, reward, done, info = env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return StepResponse(observation=obs, reward=reward, done=done, info=info)


@app.get("/state", response_model=EnvState)
def get_state():
    return env.state()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
