import os
import time
from typing import List

import requests
from django.urls import reverse
from django_rq import job
from loguru import logger

from calls.choices import EmotionalToneChoices, EMOTIONAL_TONE_LABELS
from calls.models import Call
from categories.models import Category
from categories.service import (
    get_all_candidate_labels,
    get_all_category_points,
    get_all_categories,
)
from core.storages import get_call_transcription_path


@job
def send_zero_shot_classification_request(call_id: str):
    call = Call.objects.get(id=call_id)
    request_url = os.getenv("CATEGORIZATION_URL") + "/classify"
    webhook_url = os.getenv("HOST_URL") + reverse(
        "api:zero-shot-classification-webhook",
    )

    logger.info(f"Sending zero-shot classification request for call_id: {call_id}")

    params = {"call_id": call_id}

    payload = {
        "candidate_labels": get_all_candidate_labels(),
        "context_path": get_call_transcription_path(call_id),
        "webhook_url": webhook_url,
    }

    response = requests.post(
        request_url,
        params=params,
        json=payload,
    )

    if response.status_code != 200:
        logger.error(
            f"Failed to send zero-shot classification request for call_id: {call_id}"
        )
        logger.error(response.text)


@job
def process_zero_shot_classification_response(call_id: str, response: dict):
    call = Call.objects.get(id=call_id)

    if response.get("finish_time") < call.zero_shot_classification_finish_time:
        return

    call.zero_shot_classification_finish_time = response.pop("finish_time")
    call.zero_shot_classification_worked = True

    # Emotional tone classification
    emotional_tone_values = {
        EmotionalToneChoices.positive: response.pop(
            EMOTIONAL_TONE_LABELS[EmotionalToneChoices.positive], 0
        ),
        EmotionalToneChoices.negative: response.pop(
            EMOTIONAL_TONE_LABELS[EmotionalToneChoices.negative], 0
        ),
        EmotionalToneChoices.neutral: response.pop(
            EMOTIONAL_TONE_LABELS[EmotionalToneChoices.neutral], 0
        ),
        EmotionalToneChoices.angry: response.pop(
            EMOTIONAL_TONE_LABELS[EmotionalToneChoices.angry], 0
        ),
    }

    call.emotional_tone = max(emotional_tone_values, key=emotional_tone_values.get)

    # Categories classification
    category_threshold = float(os.getenv("ZERO_SHOT_CATEGORY_THRESHOLD", 0.4))
    topics_threshold = float(os.getenv("ZERO_SHOT_TOPICS_THRESHOLD", 0.4))

    for category_id, values in get_all_categories().items():
        category = values["title"]
        points = values["points"]
        category_score = response.get(category, 0)

        points_score = 0
        for point in points:
            points_score += response.get(point, 0)

        if category_score >= category_threshold or points_score >= topics_threshold:
            call.categories.add(category_id)

    call.save()

    logger.info(f"Saved zero-shot classification result for call_id: {call_id}")


@job
def send_zero_shot_classification_request_for_specific_category(
    category_id: str,
):
    """
    Send a zero-shot classification request for a specific category to analyse calls
    The delay between calls is 20 seconds

    :param category_id: ID of the new category
    """
    category = Category.objects.get(id=category_id)
    request_url = os.getenv("CATEGORIZATION_URL") + "/classify"

    logger.info(
        f"Sending zero-shot classification request for category: {category_id} with {len(call_ids)} calls"
    )

    calls_queryset = Call.objects.filter(text__isnull=False)

    call: Call
    for call in calls_queryset:
        time.sleep(20)
        params = {"call_id": call.id}
        payload = {
            "candidate_labels": category.candidate_labels,
            "context_path": get_call_transcription_path(call.id),
            "webhook_url": os.getenv("HOST_URL")
            + reverse(
                "api:zero-shot-classification-webhook",
            ),
        }

        call.categories.remove(category_id)

        response = requests.post(
            request_url,
            params=params,
            json=payload,
        )

        if response.status_code != 200:
            logger.error(
                f"Failed to send zero-shot classification request for call_id: {call.id}"
            )
            logger.error(response.text)

    logger.info(
        f"Finished zero-shot classification request for new category: {category_id}"
    )


def send_zero_shot_classification_request_for_affected_calls(category_id: str):
    """
    Send a zero-shot classification request for a specific category to analyse related calls

    :param category_id: ID of the new category
    """

    calls = Call.objects.filter(categories=category_id)
    send_zero_shot_classification_request_for_specific_category.delay(
        category_id, list(calls.values_list("id", flat=True))
    )
