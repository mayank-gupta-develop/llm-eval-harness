import argparse
import json
import sys
from pathlib import Path

from app.pipelines import PIPELINES
from app.scorers import contains_scorer

GOLDEN_PATH = Path(__file__).resolve().parent.parent / "data" / "golden.json"


def run_gate(pipeline_name: str, threshold: float) -> int:
    pipeline = PIPELINES[pipeline_name]
    cases = json.loads(GOLDEN_PATH.read_text())
    scores = []
    for case in cases:
        actual = pipeline(case["question"])
        score = contains_scorer(case["expected_answer"], actual)
        scores.append(score)
        status = "PASS" if score >= 0.5 else "FAIL"
        print(f"[{status}] {case['question']} -> {actual!r}")

    avg = sum(scores) / len(scores)
    print(f"Pipeline: {pipeline_name}")
    print(f"Average score: {avg:.2f} (threshold {threshold:.2f})")
    if avg < threshold:
        print("GATE FAILED: quality below threshold")
        return 1
    print("GATE PASSED")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pipeline", choices=list(PIPELINES), default="good_pipeline")
    parser.add_argument("--threshold", type=float, default=0.8)
    args = parser.parse_args()
    sys.exit(run_gate(args.pipeline, args.threshold))
