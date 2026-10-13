import json
import sys
import time
from pathlib import Path

from app.pipelines import llm_pipeline
from app.scorers import contains_scorer, judge_scorer

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "data" / "golden_v2.json"
OUT = ROOT / "results" / "compare.json"


def main(delay: float = 3.0) -> int:
    cases = json.loads(GOLDEN.read_text())
    rows = []
    for c in cases:
        answer = llm_pipeline(c["question"])
        contains = contains_scorer(c["expected_answer"], answer)
        try:
            judge = judge_scorer(c["question"], c["expected_answer"], answer)
        except ValueError:
            judge = None
        rows.append(
            {
                "question": c["question"],
                "expected": c["expected_answer"],
                "answer": answer,
                "contains": contains,
                "judge": judge,
            }
        )
        print(f"contains={contains} judge={judge} | {c['expected_answer']!r} <- {answer!r}")
        time.sleep(delay)

    scored = [r for r in rows if r["judge"] is not None]
    if not scored:
        print("No cases were judged successfully")
        return 1
    disagree = [r for r in scored if r["contains"] != r["judge"]]
    print(f"\nCases: {len(rows)}  judge errors: {len(rows) - len(scored)}")
    print(f"Contains avg: {sum(r['contains'] for r in scored) / len(scored):.2f}")
    print(f"Judge avg:    {sum(r['judge'] for r in scored) / len(scored):.2f}")
    print(f"Disagreements: {len(disagree)} of {len(scored)}")
    for r in disagree:
        print(f"  contains={r['contains']} judge={r['judge']} | {r['expected']!r} <- {r['answer']!r}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
