import json
import math
import sys
import time
from collections import defaultdict
from pathlib import Path

from app.judge_eval_v2 import fmt
from app.llm import LLMError
from app.scorers import judge_scorer, judge_scorer_v2

ROOT = Path(__file__).resolve().parent.parent
HELD = ROOT / "data" / "injection_heldout.json"
BASE = ROOT / "data" / "judge_cases_v2.json"
PRIOR = ROOT / "results" / "judge_eval_v2.json"
OUT = ROOT / "results" / "judge_injection_eval.json"


def run_judge(fn, cases, runs, delay):
    out = {c["id"]: [] for c in cases}
    for _ in range(runs):
        for c in cases:
            v = None
            for attempt in range(4):
                try:
                    v = fn(c["question"], c["expected"], c["candidate"])
                    break
                except (LLMError, ValueError):
                    time.sleep(5 * (attempt + 1))
            out[c["id"]].append(v)
            time.sleep(delay)
    return out


def majority(verdicts):
    return {i: (1.0 if sum(v) / len(v) > 0.5 else 0.0) for i, v in verdicts.items() if None not in v}


def sign_test(b, c):
    n = b + c
    if n == 0:
        return 1.0
    k = min(b, c)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def show(name, cases, verdicts):
    truth = {c["id"]: 1.0 if c["correct"] else 0.0 for c in cases}
    vote = majority(verdicts)
    hit = sum(vote[i] == truth[i] for i in vote)
    same = sum(len(set(verdicts[i])) == 1 for i in vote)
    print(f"{name}: majority {fmt(hit, len(vote))} | identical across runs {same}/{len(vote)} | missing {len(cases) - len(vote)}")
    return vote


def main(runs=3, delay=1.5):
    held = json.loads(HELD.read_text(encoding="utf-8"))
    base = json.loads(BASE.read_text(encoding="utf-8"))
    prior = {c["id"]: c["judge"] for c in json.loads(PRIOR.read_text(encoding="utf-8"))["cases"]}
    dev = [c for c in base if c["category"] == "injection"]
    normal = [c for c in base if c["category"] != "injection"]

    v1_held = run_judge(judge_scorer, held, runs, delay)
    print("held-out, original prompt: done", flush=True)
    v2_held = run_judge(judge_scorer_v2, held, runs, delay)
    print("held-out, hardened prompt: done", flush=True)
    v2_dev = run_judge(judge_scorer_v2, dev, runs, delay)
    v2_normal = run_judge(judge_scorer_v2, normal, runs, delay)
    print("regression cases: done", flush=True)

    truth = {c["id"]: 1.0 if c["correct"] else 0.0 for c in held}
    print(f"\n== Held-out injection cases: {len(held)} new, never used to design the hardened prompt ==")
    m1 = show("original prompt", held, v1_held)
    m2 = show("hardened prompt", held, v2_held)
    both = [i for i in truth if i in m1 and i in m2]
    fixed = sum(m1[i] != truth[i] and m2[i] == truth[i] for i in both)
    broke = sum(m1[i] == truth[i] and m2[i] != truth[i] for i in both)
    print(f"Hardened fixed {fixed} cases and broke {broke} (exact sign test p = {sign_test(fixed, broke):.3f})")

    print("\nBy attack style (majority vote, original vs hardened):")
    styles = defaultdict(list)
    for c in held:
        styles[c["style"]].append(c["id"])
    for s, ids in styles.items():
        a = sum(m1.get(i) == truth[i] for i in ids)
        b = sum(m2.get(i) == truth[i] for i in ids)
        print(f"  {s:13s} original {a}/{len(ids)}   hardened {b}/{len(ids)}")

    print("\nHardened prompt misses on held-out cases:")
    for c in held:
        if m2.get(c["id"]) != truth[c["id"]]:
            print(f"  #{c['id']} {c['style']} label={'correct' if c['correct'] else 'wrong'} votes={v2_held[c['id']]} | {c['candidate'][:60]!r}")

    print("\n== Original 6 injection cases (used while designing the hardened prompt, so not a clean test) ==")
    show("original prompt (earlier run)", dev, {c["id"]: prior[c["id"]] for c in dev})
    show("hardened prompt", dev, v2_dev)
    print(f"\n== Regression check: {len(normal)} non-injection cases ==")
    show("original prompt (earlier run)", normal, {c["id"]: prior[c["id"]] for c in normal})
    show("hardened prompt", normal, v2_normal)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({"runs": runs, "held_out": [{**c, "original": v1_held[c["id"]], "hardened": v2_held[c["id"]]} for c in held], "dev": {str(k): v for k, v in v2_dev.items()}, "regression": {str(k): v for k, v in v2_normal.items()}}, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
