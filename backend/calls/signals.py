from django.db.models.signals import post_save
from django.dispatch import receiver

from calls.models import Call
from calls.tasks import send_transcription_request, send_qa_request
from categories.tasks import send_zero_shot_classification_request


@receiver(post_save, sender=Call)
def post_save_call(sender, instance, created, **kwargs):
    update_fields = kwargs.get("update_fields")
    if created:
        send_transcription_request.delay(instance.id)

    if update_fields and "text" in update_fields:
        send_qa_request(call_id=instance.id, question_type="name")
        send_qa_request(call_id=instance.id, question_type="location")
        send_zero_shot_classification_request.delay(instance.id)
