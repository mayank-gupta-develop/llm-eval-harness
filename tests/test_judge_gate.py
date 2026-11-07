import json

import app.judge_gate as gate
from app.llm import LLMError


def _truth():
    cases = json.loads(gate.HELD.read_text(encoding="utf-8")) + json.loads(gate.BASE.read_text(encoding="utf-8"))
    return {(c["question"], c["expected"], c["candidate"]): 1.0 if c["correct"] else 0.0 for c in cases}


def _run(monkeypatch, fake):
    monkeypatch.setitem(gate.JUDGES, "v2", fake)
    monkeypatch.setattr(gate.time, "sleep", lambda s: None)
    return gate.main(version="v2", delay=0)


def test_gate_passes_for_a_judge_that_matches_the_labels(monkeypatch):
    truth = _truth()
    assert _run(monkeypatch, lambda q, e, a: truth[(q, e, a)]) == 0


def test_gate_fails_for_a_judge_that_accepts_everything(monkeypatch):
    assert _run(monkeypatch, lambda q, e, a: 1.0) == 1


def test_gate_fails_when_the_judge_returns_no_verdicts(monkeypatch):
    def broken(q, e, a):
        raise LLMError("down")

    assert _run(monkeypatch, broken) == 1
