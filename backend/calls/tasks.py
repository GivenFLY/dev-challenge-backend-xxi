import os

import requests
from django.urls import reverse
from django_rq import job
from loguru import logger

from calls.models import Call
from core.storages import get_call_transcription_path


@job
def send_transcription_request(call_id: str):
    request_url = os.getenv("SPEECH_TO_TEXT_URL") + "/transcribe"
    call = Call.objects.get(id=call_id)
    webhook_url = os.getenv("HOST_URL") + reverse("api:speech-to-text-webhook")

    logger.info(f"Sending transcription request for call_id: {call_id}")
    requests.post(
        request_url,
        params={
            "call_id": call_id,
            "audio_path": call.audio.path,
            "webhook_url": webhook_url,
        },
    )


@job
def save_transcription_text(call_id: str, transcription_path: str):
    if not os.path.exists(transcription_path):
        logger.error(f"Transcription file not found: {transcription_path}")
        return

    call = Call.objects.get(id=call_id)

    with open(transcription_path, "r", encoding="utf-8") as transcription_file:
        transcription = transcription_file.read()
        call.text = transcription
        call.transcription_worked = True
        call.save(update_fields=["text", "transcription_worked"])

    logger.info(f"Saved transcription for call_id: {call_id}")


@job
def send_qa_request(call_id: str, question_type: str):
    request_url = os.getenv("CATEGORIZATION_URL") + "/qa"
    webhook_url = os.getenv("HOST_URL") + reverse(
        "api:question-answering-webhook",
    )

    # Define question and webhook query parameter based on type
    question_env_var = f"{question_type.upper()}_QUESTION"
    default_question = f"Get the {question_type} of the person who makes the call?"
    question = os.getenv(question_env_var, default_question)
    webhook_query_param = f"?question={question_type}"

    # Log the question type
    logger.info(
        f"Sending {question_type} question answering request for call_id: {call_id}"
    )

    params = {"call_id": call_id}
    payload = {
        "question": question,
        "context_path": get_call_transcription_path(call_id),
        "webhook_url": webhook_url + webhook_query_param,
    }
    logger.info(payload)

    response = requests.post(
        request_url,
        params=params,
        json=payload,
    )

    if response.status_code != 200:
        logger.error(
            f"Failed to send {question_type} question answering request for call_id: {call_id}"
        )
        logger.error(response.text)


@job
def save_qa_response(call_id: str, question_type: str, answer: str, score: str):
    call = Call.objects.get(id=call_id)

    name_threshold = os.getenv("NAME_THRESHOLD", 0.2)
    location_threshold = os.getenv("LOCATION_THRESHOLD", 0.2)

    if question_type == "name":
        if score >= name_threshold:
            call.name = answer
        call.qa_for_name_worked = True

    if question_type == "location":
        if score >= location_threshold:
            call.location = answer
        call.qa_for_location_worked = True

    call.save(
        update_fields=[
            "name",
            "location",
            "qa_for_name_worked",
            "qa_for_location_worked",
        ]
    )

    logger.info(f"Saved QA response for call_id: {call_id}")
