from django.db import models


class CallStatusChoices(models.TextChoices):
    pending = "pending"
    transcribing = "transcribing"
    categorizing = "categorizing"
    done = "done"
    error = "error"


class EmotionalToneChoices(models.TextChoices):
    neutral = "neutral"
    positive = "positive"
    negative = "negative"
    angry = "angry"


EMOTIONAL_TONE_LABELS = {
    EmotionalToneChoices.neutral: "Neutral",
    EmotionalToneChoices.positive: "Positive",
    EmotionalToneChoices.negative: "Negative",
    EmotionalToneChoices.angry: "Angry",
}
