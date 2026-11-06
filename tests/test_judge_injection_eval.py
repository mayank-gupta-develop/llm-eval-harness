from app.judge_injection_eval import sign_test


def test_sign_test_values():
    assert sign_test(5, 0) == 0.0625
    assert sign_test(3, 3) == 1.0
    assert sign_test(0, 0) == 1.0
