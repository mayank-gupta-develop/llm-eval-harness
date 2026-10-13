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


def test_unicode_spaces_are_normalized():
    assert contains_scorer("Leonardo da Vinci", "Leonardo da\u202fVinci painted it.") == 1.0


def test_whole_word_match_only():
    assert contains_scorer("7", "There are 17 continents.") == 0.0
    assert contains_scorer("No", "Yes, it is not hard to see it.") == 0.0


def test_hyphen_counts_as_space():
    assert contains_scorer("forty-four", "forty four") == 1.0
