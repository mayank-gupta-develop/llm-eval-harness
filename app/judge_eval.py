import json
import sys
import time
from pathlib import Path

from app.scorers import contains_scorer, judge_scorer

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "data" / "judge_cases.json"
OUT = ROOT / "results" / "judge_eval.json"


def report(name, rows):
    right = [r for r in rows if r[name] == (1.0 if r["correct"] else 0.0)]
    fp = [r for r in rows if r[name] == 1.0 and not r["correct"]]
    fn = [r for r in rows if r[name] == 0.0 and r["correct"]]
    print(f"{name}: {len(right)}/{len(rows)} match labels | false positives {len(fp)} | false negatives {len(fn)}")
    for r in fp:
        print(f"  FALSE POSITIVE: {r['expected']!r} <- {r['candidate']!r}")
    for r in fn:
        print(f"  FALSE NEGATIVE: {r['expected']!r} <- {r['candidate']!r}")


def main(delay: float = 2.0) -> int:
    rows = []
    for c in json.loads(CASES.read_text()):
        contains = contains_scorer(c["expected"], c["candidate"])
        try:
            judge = judge_scorer(c["question"], c["expected"], c["candidate"])
        except ValueError:
            judge = None
        rows.append({**c, "contains": contains, "judge": judge})
        time.sleep(delay)

    scored = [r for r in rows if r["judge"] is not None]
    print(f"Cases: {len(rows)}  judge format errors: {len(rows) - len(scored)}\n")
    report("contains", scored)
    print()
    report("judge", scored)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
