KNOWN_ANSWERS = {
    "What is the capital of France?": "Paris",
    "What is the capital of Japan?": "Kyoto",
}


def fake_pipeline(question: str) -> str:
    return KNOWN_ANSWERS.get(question, "I don't know")


def good_pipeline(question: str) -> str:
    answers = dict(KNOWN_ANSWERS)
    answers["What is the capital of Japan?"] = "Tokyo"
    return answers.get(question, "I don't know")


PIPELINES = {
    "fake_pipeline": fake_pipeline,
    "good_pipeline": good_pipeline,
}
