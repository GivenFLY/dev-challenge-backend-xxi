import json

from transformers import pipeline


def preload_model():
    with open("config.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    pipeline(
        "zero-shot-classification",
        model=data.get("zero_shot_model", "facebook/bart-large-mnli"),
    )
    pipeline(
        "question-answering", model=data.get("qa_model", "deepset/roberta-base-squad2")
    )


if __name__ == "__main__":
    preload_model()
