from app.judge_eval_v2 import wilson


def test_wilson_matches_known_value():
    lo, hi = wilson(50, 100)
    assert abs(lo - 0.4038) < 0.001 and abs(hi - 0.5962) < 0.001


def test_wilson_handles_empty_and_extremes():
    assert wilson(0, 0) == (0.0, 0.0)
    lo, hi = wilson(60, 60)
    assert 0.9 < lo < 1.0 and abs(hi - 1.0) < 1e-9
