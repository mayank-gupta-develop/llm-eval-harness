from app.scorers import contains_scorer, normalize


def test_exact_match_scores_one():
    assert contains_scorer("Paris", "Paris") == 1.0


def test_match_ignores_case_and_punctuation():
    assert contains_scorer("Paris", "The capital is paris!") == 1.0


def test_wrong_answer_scores_zero():
    assert contains_scorer("Tokyo", "Kyoto") == 0.0


def test_dont_know_scores_zero():
    assert contains_scorer("Paris", "I don't know") == 0.0


def test_normalize_strips_punctuation():
    assert normalize("  Hello, World! ") == "hello world"
