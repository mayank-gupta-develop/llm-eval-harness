import re
import unicodedata

from app.llm import chat


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    text = re.sub(r"[-\u2010-\u2015]", " ", text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    return " ".join(text.split())


def contains_scorer(expected: str, actual: str) -> float:
    e, a = normalize(expected), normalize(actual)
    return 1.0 if f" {e} " in f" {a} " else 0.0


JUDGE_MODEL = "openai/gpt-oss-120b"


def judge_scorer(question: str, expected: str, actual: str) -> float:
    prompt = (
        "You are grading an answer.\n"
        f"Question: {question}\n"
        f"Reference answer: {expected}\n"
        f"Candidate answer: {actual}\n"
        "Reply with exactly one word: CORRECT if the candidate answer agrees "
        "with the reference answer, otherwise INCORRECT."
    )
    verdict = chat(JUDGE_MODEL, prompt).strip().upper()
    if not verdict.startswith(("CORRECT", "INCORRECT")):
        raise ValueError(f"Unexpected judge reply: {verdict[:80]!r}")
    return 1.0 if verdict.startswith("CORRECT") else 0.0
