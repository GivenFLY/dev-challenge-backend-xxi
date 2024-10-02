import os.path

from core import settings


def get_call_transcription_path(call_id: str) -> str:
    """
    Get the path to the audio file for a given call ID

    :param call_id: Call ID
    :return: Path to the audio file
    """
    return os.path.join(settings.EXTERNAL_MEDIA_STORAGE_ROOT, "calls", f"{call_id}.txt")


def save_transcription(call_id: str, transcription: str) -> str:
    """
    Save the transcription for a given call ID

    :param call_id: Call ID
    :param transcription: Transcription of the call
    :return: Path to the saved transcription
    """

    path = get_call_transcription_path(call_id)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding='utf-8') as f:
        f.write(transcription)

    return path
