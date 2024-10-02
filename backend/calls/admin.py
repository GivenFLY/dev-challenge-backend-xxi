from django.contrib import admin

from calls.models import Call
from calls.tasks import send_qa_request
from categories.tasks import send_zero_shot_classification_request


@admin.register(Call)
class CallAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "location",
        "emotional_tone",
        "transcription_worked",
        "zero_shot_classification_worked",
        "qa_for_name_worked",
        "qa_for_location_worked",
    )
    search_fields = ("name", "location")
    list_filter = ("emotional_tone",)
    filter_horizontal = ("categories",)

    fieldsets = (
        (
            "Work status",
            {
                "fields": (
                    (
                        "transcription_worked",
                        "zero_shot_classification_worked",
                        "qa_for_name_worked",
                        "qa_for_location_worked",
                    ),
                    ("zero_shot_classification_finish_time",),
                )
            },
        ),
        (
            None,
            {
                "fields": (
                    "audio",
                    "name",
                    "location",
                    "emotional_tone",
                    "categories",
                    "text",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        if obj.id and change and "text" in form.changed_data:
            obj.qa_for_name_worked = False
            obj.qa_for_location_worked = False
            obj.name = ""
            obj.location = ""
            obj.categories.clear()
            send_qa_request(call_id=obj.id, question_type="name")
            send_qa_request(call_id=obj.id, question_type="location")
            send_zero_shot_classification_request.delay(obj.id)
            obj.save(update_fields=["qa_for_name_worked", "qa_for_location_worked"])

        super().save_model(request, obj, form, change)
