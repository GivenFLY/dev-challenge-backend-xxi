import json

from transformers import pipeline


def preload_model():
    with open("config.json", "r", encoding='utf-8') as f:
        data = json.loads(f.read())
    pipeline("automatic-speech-recognition", model=data.get("model", "openai/whisper-tiny.en"))


if __name__ == "__main__":
    preload_model()
