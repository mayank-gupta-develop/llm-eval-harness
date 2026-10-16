import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

from app.llm import LLMError
from app.scorers import contains_scorer, judge_scorer

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "data" / "judge_cases_v2.json"
OUT = ROOT / "results" / "judge_eval_v2.json"


def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)


def fmt(k, n):
    lo, hi = wilson(k, n)
    return f"{k}/{n} = {k / n:.0%} (95% CI {lo:.0%} to {hi:.0%})"


def judge_once(c):
    for attempt in range(4):
        try:
            return judge_scorer(c["question"], c["expected"], c["candidate"])
        except (LLMError, ValueError):
            time.sleep(5 * (attempt + 1))
    return None


def main(runs=3, delay=1.5):
    cases = json.loads(CASES.read_text(encoding="utf-8"))
    truth = {c["id"]: 1.0 if c["correct"] else 0.0 for c in cases}
    base = {c["id"]: contains_scorer(c["expected"], c["candidate"]) for c in cases}
    verdicts = {c["id"]: [] for c in cases}
    for r in range(runs):
        for c in cases:
            verdicts[c["id"]].append(judge_once(c))
            time.sleep(delay)
        print(f"run {r + 1}/{runs} finished", flush=True)

    n = len(cases)
    print(f"\nCases: {n} ({sum(truth.values()):.0f} labeled correct), judge runs: {runs}")
    print("Whole-word baseline:", fmt(sum(base[i] == truth[i] for i in truth), n))
    for r in range(runs):
        got = [i for i in truth if verdicts[i][r] is not None]
        print(f"Judge run {r + 1}:", fmt(sum(verdicts[i][r] == truth[i] for i in got), len(got)), f"| no verdict: {n - len(got)}")

    full = [i for i in truth if None not in verdicts[i]]
    vote = {i: 1.0 if sum(verdicts[i]) / runs > 0.5 else 0.0 for i in full}
    stable = [i for i in full if len(set(verdicts[i])) == 1]
    print(f"Cases with a verdict in every run: {len(full)}/{n}")
    print(f"Same verdict in all runs: {len(stable)}/{len(full)}")
    print("Judge majority vote:", fmt(sum(vote[i] == truth[i] for i in full), len(full)))

    cats = defaultdict(list)
    for c in cases:
        cats[c["category"]].append(c["id"])
    print("\nBy category (judge majority vote vs whole-word baseline):")
    for cat, ids in cats.items():
        j = sum(vote.get(i) == truth[i] for i in ids)
        b = sum(base[i] == truth[i] for i in ids)
        print(f"  {cat:14s} judge {j}/{len(ids)}   whole-word {b}/{len(ids)}")

    print("\nJudge misses (majority vote, or no verdict):")
    for c in cases:
        if vote.get(c["id"]) != truth[c["id"]]:
            print(f"  #{c['id']} {c['category']} label={'correct' if c['correct'] else 'wrong'} votes={verdicts[c['id']]} | {c['expected']!r} <- {c['candidate'][:70]!r}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"runs": runs, "cases": [{**c, "judge": verdicts[c["id"]], "whole_word": base[c["id"]]} for c in cases]}, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
