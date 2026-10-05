import re


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", text.lower()).strip()


def contains_scorer(expected: str, actual: str) -> float:
    return 1.0 if normalize(expected) in normalize(actual) else 0.0
