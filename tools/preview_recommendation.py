from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON_PATH = ROOT / "common"
if str(COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_PATH))

from aegis_common.rule_test_runner import evaluate_single_metrics, load_sample

def main() -> None:
    parser = argparse.ArgumentParser(description="Preview recommendation output for one metrics sample.")
    parser.add_argument("sample", help="Path to a sample JSON file containing a metrics object")
    parser.add_argument("--profile", default="default_recommendation_rules", help="Recommendation rule profile name")
    parser.add_argument("--rule-dir", default=str(ROOT / "recommendation_rules"), help="Directory containing recommendation rule profiles")
    args = parser.parse_args()

    sample = load_sample(args.sample)
    report = evaluate_single_metrics(
        metrics=sample["metrics"],
        profile_name=args.profile,
        rule_dir=args.rule_dir,
    )
    report["sample_id"] = sample["sample_id"]
    report["expected_issue_ids"] = sample.get("expected_issue_ids", [])
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
