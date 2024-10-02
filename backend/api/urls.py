from django.urls import path

from calls.views import (
    CallCreateAPIView,
    CallRetrieveAPIView,
    SpeechToTextWebhookAPIView,
    QAWebhookAPIView,
)
from categories.views import (
    CategoryListCreateAPIView,
    CategoryRetrieveUpdateDestroyAPIView,
    ZeroShotClassificationWebhookAPIView,
)

urlpatterns = [
    path("category/", CategoryListCreateAPIView.as_view(), name="category-list-create"),
    path(
        "category/<uuid:pk>/",
        CategoryRetrieveUpdateDestroyAPIView.as_view(),
        name="category-retrieve-update-destroy",
    ),
    path("call/", CallCreateAPIView.as_view(), name="call-list-create"),
    path("call/<int:pk>/", CallRetrieveAPIView.as_view(), name="call-retrieve"),
    path(
        "speech_to_text_webhook/",
        SpeechToTextWebhookAPIView.as_view(),
        name="speech-to-text-webhook",
    ),
    path(
        "question_answering_webhook/",
        QAWebhookAPIView.as_view(),
        name="question-answering-webhook",
    ),
    path(
        "zero_shot_classification_webhook/",
        ZeroShotClassificationWebhookAPIView.as_view(),
        name="zero-shot-classification-webhook",
    ),
]
