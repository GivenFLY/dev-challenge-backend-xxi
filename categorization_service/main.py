from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response
from pydantic import BaseModel

from core.consts import RequestStatuses
from core.manager import RedisManager

app = FastAPI()


class TaskBody(BaseModel):
    context: str = None
    context_path: str = None
    candidate_labels: List[str] = None
    question: str = None
    webhook_url: str = None


@app.post("/classify")
async def create_classification_task(call_id: str, body: TaskBody):
    """
    Endpoint to create a classification task.
    """
    validate_context(body)
    return await process_task(call_id, body, "zero_shot_classification")


@app.post("/qa")
async def create_qa_task(call_id: str, body: TaskBody):
    """
    Endpoint to create a question-answering task.
    """
    validate_context(body)
    return await process_task(call_id, body, "question_answering")


def validate_context(body):
    if not body.context and not body.context_path:
        raise HTTPException(
            status_code=400, detail="Either context or context_path must be provided."
        )


async def process_task(call_id, body, job_type):
    await RedisManager.set_job_status(call_id, "pending")
    redis = await RedisManager.get_pool()
    job_args = [
        call_id,
        (
            body.candidate_labels
            if job_type == "zero_shot_classification"
            else body.question
        ),
        body.context,
        body.context_path,
        body.webhook_url,
    ]
    await redis.enqueue_job(job_type, *job_args)
    return {"message": f"{job_type.replace('_', ' ').title()} job submitted."}


@app.exception_handler(ConnectionError)
async def connection_error_handler(request, exc):
    await RedisManager.delete_job_status(request.body().call_id)
    return HTTPException(
        status_code=503,
        detail="Service temporarily unavailable. Please try again later.",
    )
