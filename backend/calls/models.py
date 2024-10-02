from django.db import models

from calls.choices import CallStatusChoices, EmotionalToneChoices
from core.storages import ExternalMediaStorage

external_media_storage = ExternalMediaStorage()


class Call(models.Model):
    audio = models.FileField(storage=external_media_storage, upload_to="audio/")
    name = models.CharField(max_length=512, blank=True, null=True)
    location = models.CharField(max_length=512, blank=True, null=True)
    emotional_tone = models.CharField(
        max_length=32, choices=EmotionalToneChoices.choices, blank=True, null=True
    )
    text = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(
        "categories.Category", related_name="calls", blank=True
    )

    transcription_worked = models.BooleanField(default=False)

    zero_shot_classification_worked = models.BooleanField(default=False)
    zero_shot_classification_finish_time = models.BigIntegerField(default=0)

    qa_for_name_worked = models.BooleanField(default=False)
    qa_for_location_worked = models.BooleanField(default=False)

    @property
    def is_ready(self):
        return (
            self.transcription_worked
            and self.zero_shot_classification_worked
            and self.qa_for_name_worked
            and self.qa_for_location_worked
        )
