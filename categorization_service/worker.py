import asyncio
import json
import os
import time
from typing import List

import requests
from arq import Worker
from arq.connections import RedisSettings
from transformers import pipeline

from core.consts import RequestStatuses, logger
from core.manager import RedisManager


with open("config.json") as f:
    config = json.load(f)

zero_shot_pipeline = pipeline(
    "zero-shot-classification",
    model=config.get("zero_shot_model", "facebook/bart-large-mnli"),
)

question_answering_pipeline = pipeline(
    "question-answering",
    model=config.get("qa_model", "deepset/roberta-base-squad2"),
)


def send_webhook(webhook_url: str, call_id: str, response: dict):
    """
    Send a webhook to a given URL with the transcription path

    :param webhook_url: Webhook URL
    :param call_id: Call ID
    :param response: Response from the zero-shot classification
    :return: None
    """
    data = {"call_id": call_id, "result": response}
    requests.post(webhook_url, json=data)


async def zero_shot_classification(
    ctx,
    call_id: str,
    candidate_labels: List[str],
    context: str = None,
    context_path: str = None,
    webhook_url: str = None,
):
    """
    Transcribe an audio file and save the transcription to a file

    :param ctx: ARQ context
    :param call_id: Call ID
    :param candidate_labels: Candidate labels for the categorization
    :param context: Context for the categorization (optional, but one of context or context_path must be provided)
    :param context_path: Path to the context file (optional, but one of context or context_path must be provided)
    :param webhook_url: URL to send a webhook to
    :return: None
    """
    try:
        if not context and not context_path:
            raise ValueError("Either context or context_path must be provided.")

        if context_path:
            with open(context_path, "r", encoding="utf-8") as context_file:
                context = context_file.read()

        logger.info(f"Starting classification for call_id: {call_id}")
        await RedisManager.set_job_status(call_id, RequestStatuses.Processing)
        result = zero_shot_pipeline(context, candidate_labels, multilabel=True)
        response = {
            result["labels"][i]: result["scores"][i]
            for i in range(len(result["labels"]))
        }
        response["finish_time"] = time.time_ns()
        await RedisManager.set_job_status(call_id, RequestStatuses.Done)
        logger.info(f"Completed classification for call_id: {call_id}")
        logger.info(f"Transcription result:")
        logger.info(json.dumps(response, indent=2))
        if webhook_url:
            logger.info(f"Sending webhook ({webhook_url!s}) for call_id: {call_id}")
            send_webhook(webhook_url, call_id, response)

    except Exception as e:
        await RedisManager.set_job_status(call_id, RequestStatuses.Failed)
        logger.error(f"Failed to transcribe call_id: {call_id}")
        logger.exception(e)
        raise e


async def question_answering(
    ctx,
    call_id: str,
    question: str,
    context: str = None,
    context_path: str = None,
    webhook_url: str = None,
):
    """
    Transcribe an audio file and save the transcription to a file

    :param ctx: ARQ context
    :param call_id: Call ID
    :param question: Question to ask
    :param context: Context for the question answering (optional, but one of context or context_path must be provided)
    :param context_path: Path to the context file (optional, but one of context or context_path must be provided)
    :param webhook_url: URL to send a webhook to
    :return: None
    """
    try:
        if not context and not context_path:
            raise ValueError("Either context or context_path must be provided.")

        if context_path:
            with open(context_path, "r", encoding="utf-8") as context_file:
                context = context_file.read()

        logger.info(f"Starting question answering for call_id: {call_id}")
        await RedisManager.set_job_status(call_id, RequestStatuses.Processing)
        qa_input = {"question": question, "context": context}
        result = question_answering_pipeline(qa_input)
        await RedisManager.set_job_status(call_id, RequestStatuses.Done)
        logger.info(f"Completed question answering for call_id: {call_id}")
        logger.info(f"Question Answering result:")
        logger.info(json.dumps(result, indent=2))
        if webhook_url:
            logger.info(f"Sending webhook ({webhook_url!s}) for call_id: {call_id}")
            send_webhook(webhook_url, call_id, result)

    except Exception as e:
        await RedisManager.set_job_status(call_id, RequestStatuses.Failed)
        logger.error(f"Failed to transcribe call_id: {call_id}")
        logger.exception(e)
        raise e


async def main():
    """
    Main function to run the worker

    :return: None
    """
    await RedisManager.delete_all_jobs()

    w = Worker(
        functions=[zero_shot_classification, question_answering],
        redis_settings=RedisSettings(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            database=int(os.getenv("REDIS_DB", 2)),
            conn_timeout=300,
            max_connections=10,
        ),
        max_jobs=int(os.getenv("WORKER_MAX_JOBS", 100)),
        job_timeout=int(os.getenv("WORKER_JOB_TIMEOUT", 3600)),
        max_tries=int(os.getenv("WORKER_MAX_TRIES", 20)),
        log_results=True,
    )
    await w.main()


if __name__ == "__main__":
    asyncio.run(main())
