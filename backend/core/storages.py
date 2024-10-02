import os

from django.core.files.storage import FileSystemStorage
from django.conf import settings


class ExternalMediaStorage(FileSystemStorage):
    """
    Custom storage class for external media files
    """

    def __init__(
        self,
        location=settings.EXTERNAL_MEDIA_STORAGE_ROOT,
        base_url=settings.EXTERNAL_MEDIA_STORAGE_URL,
    ):
        super().__init__(location, base_url)


def get_call_transcription_path(call_id: str) -> str:
    """
    Get the path to the audio file for a given call ID

    :param call_id: Call ID
    :return: Path to the audio file
    """
    return os.path.join(settings.EXTERNAL_MEDIA_STORAGE_ROOT, "calls", f"{call_id}.txt")
