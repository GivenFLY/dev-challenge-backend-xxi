from fastapi import FastAPI, Depends, HTTPException, Response

from core.consts import RequestStatuses
from core.manager import RedisManager

app = FastAPI()


@app.post("/transcribe")
async def create_transcription_task(
    call_id: str, audio_path: str, webhook_url: str = None
):
    """
    Create a transcription task for a given call ID and audio file path

    :param call_id: Call ID
    :param audio_path: Path to the audio file
    :param webhook_url: URL to send the transcription path to
    :return: Message indicating the status of the transcription job
    """
    try:
        status = await RedisManager.get_job_status(call_id)
        if status and status != RequestStatuses.Failed:
            return Response(
                status_code=202,
                content={
                    "message": f"Transcription is already in progress. Status: {status}"
                },
            )

        await RedisManager.set_job_status(call_id, "pending")

        redis = await RedisManager.get_pool()

        await redis.enqueue_job("transcribe_audio", call_id, audio_path, webhook_url)

        return {"message": "Transcription job submitted."}

    except ConnectionError:
        await RedisManager.delete_job_status(call_id)
        raise HTTPException(
            status_code=503,
            detail="Service temporarily unavailable. Please try again later.",
        )
