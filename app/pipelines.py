KNOWN_ANSWERS = {
    "What is the capital of France?": "Paris",
    "What is the capital of Japan?": "Kyoto",
}


def fake_pipeline(question: str) -> str:
    return KNOWN_ANSWERS.get(question, "I don't know")
