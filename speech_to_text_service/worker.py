import asyncio
import json
import os

import requests
from arq import Worker
from arq.connections import RedisSettings
from transformers import pipeline

from core.consts import RequestStatuses, logger
from core.manager import RedisManager
from core.storage import save_transcription, get_call_transcription_path


with open("config.json") as f:
    config = json.load(f)
    whisper = pipeline(
        "automatic-speech-recognition", config.get("model", "openai/whisper-tiny.en")
    )


def send_webhook(webhook_url: str, call_id: str):
    """
    Send a webhook to a given URL with the transcription path

    :param webhook_url: Webhook URL
    :param call_id: Call ID
    :return: None
    """
    transcription_path = get_call_transcription_path(call_id)
    data = {"call_id": call_id, "transcription_path": transcription_path}
    requests.post(webhook_url, json=data)


async def transcribe_audio(ctx, call_id: str, audio_path: str, webhook_url: str = None):
    """
    Transcribe an audio file and save the transcription to a file

    :param ctx: ARQ context
    :param call_id: Call ID
    :param audio_path: Path to the audio file
    :param webhook_url: URL to send the transcription path to
    :return: None
    """
    if os.path.exists(get_call_transcription_path(call_id)):
        logger.info(f"Transcription already exists for call_id: {call_id}")
        await RedisManager.set_job_status(call_id, RequestStatuses.Done)
        return

    try:
        logger.info(f"Starting transcription for call_id: {call_id}")
        await RedisManager.set_job_status(call_id, RequestStatuses.Processing)
        transcription = whisper(audio_path, return_timestamps=True)["text"]

        save_transcription(call_id, transcription)
        await RedisManager.set_job_status(call_id, RequestStatuses.Done)
        logger.info(f"Completed transcription for call_id: {call_id}")
        if webhook_url:
            logger.info(f"Sending webhook for call_id: {call_id}")
            send_webhook(webhook_url, call_id)

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
        functions=[transcribe_audio],
        redis_settings=RedisSettings(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            database=int(os.getenv("REDIS_DB", 1)),
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
