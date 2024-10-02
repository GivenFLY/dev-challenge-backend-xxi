import io

import requests
from django.core.files.base import ContentFile
from loguru import logger

from rest_framework import generics, status
from rest_framework.response import Response

from calls.choices import CallStatusChoices
from calls.models import Call
from calls.serializers import (
    CallCreateSerializer,
    CallCreatedSerializer,
    CallDetailSerializer,
)
from calls.tasks import save_transcription_text, save_qa_response


class CallCreateAPIView(generics.CreateAPIView):
    queryset = Call.objects.all()
    serializer_class = CallCreateSerializer
    max_size = 300 * 1024 * 1024  # 300 MB in bytes
    allowed_mime_types = [
        "audio/mpeg",
        "audio/wav",
        "audio/mp3",
    ]  # MIME types for MP3 and WAV

    def post(self, request, *args, **kwargs):
        audio_url = request.data.get("audio_url")

        if not audio_url:
            return Response(
                {"detail": "audio_url is required"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        try:
            audio = requests.get(audio_url, stream=True)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error while fetching the audio file: {e}")
            return Response(
                {"detail": "Error while fetching the audio file"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        if audio.status_code != 200:
            return Response(
                {"detail": "Invalid audio URL"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        # Validate audio format
        validation_error = self.validate_audio_format(audio)
        if validation_error:
            return validation_error

        # Validate audio size
        result = self.validate_audio_size(audio)
        if isinstance(result, Response):
            return result

        # Save the content if size and format are valid
        audio_content = result
        audio_content.seek(0)
        content_file = ContentFile(audio_content.read())
        content_file.name = audio_url.split("/")[-1]

        # Save the audio file to the model
        call = Call.objects.create(audio=content_file)
        serializer = CallCreatedSerializer(call)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def validate_audio_size(self, audio):
        """
        Validate that the audio file size does not exceed the specified max_size.
        """
        content_length = audio.headers.get("Content-Length")

        if content_length and int(content_length) > self.max_size:
            return Response(
                {"detail": "File size exceeds the limit of 300 MB"},
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            )

        downloaded_size = 0
        chunk_size = 1024
        result = io.BytesIO()

        for chunk in audio.iter_content(chunk_size=chunk_size):
            result.write(chunk)
            downloaded_size += len(chunk)
            if downloaded_size > self.max_size:
                return Response(
                    {"detail": "File size exceeds the limit of 300 MB"},
                    status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                )
        return result

    def validate_audio_format(self, audio):
        """
        Validate that the audio file is either in MP3 or WAV format.
        """
        mime_type = audio.headers.get("Content-Type")

        # Check the MIME type against allowed MIME types
        if mime_type not in self.allowed_mime_types:
            return Response(
                {"detail": "Invalid audio format. Only MP3 or WAV are allowed."},
                status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        return None


class CallRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Call.objects.all()
    serializer_class = CallDetailSerializer

    def get(self, request, *args, **kwargs):
        instance = self.get_object()

        if not instance.is_ready:
            return Response(
                {"detail": "Transcription is not ready yet"},
                status=status.HTTP_202_ACCEPTED,
            )

        return super().get(request, *args, **kwargs)


class SpeechToTextWebhookAPIView(generics.GenericAPIView):
    serializer_class = CallCreateSerializer  # Dummy serializer

    def post(self, request, *args, **kwargs):
        call_id = request.data.get("call_id")
        transcription_path = request.data.get("transcription_path")

        if not call_id or not transcription_path:
            logger.error("Invalid webhook data")
            return Response(status=status.HTTP_204_NO_CONTENT)

        save_transcription_text.delay(call_id, transcription_path)

        return Response(status=status.HTTP_200_OK)


class QAWebhookAPIView(generics.GenericAPIView):
    serializer_class = CallCreateSerializer  # Dummy serializer

    def post(self, request, *args, **kwargs):
        call_id = request.data.get("call_id")
        result = request.data.get("result")
        score = result.get("score")
        answer = result.get("answer")

        question_type = request.query_params.get("question")

        if not call_id or not result or not score or not answer or not question_type:
            logger.error("Invalid webhook data")
            return Response(status=status.HTTP_204_NO_CONTENT)

        save_qa_response.delay(call_id, question_type, answer, score)

        return Response(status=status.HTTP_200_OK)
