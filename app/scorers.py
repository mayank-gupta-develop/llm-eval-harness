import re
import unicodedata


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", unicodedata.normalize("NFKC", text).lower()).strip()


def contains_scorer(expected: str, actual: str) -> float:
    return 1.0 if normalize(expected) in normalize(actual) else 0.0


from app.llm import chat  # noqa: E402

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
