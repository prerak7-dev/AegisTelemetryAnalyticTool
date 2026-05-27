from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMON_PATH = ROOT / "common"
if str(COMMON_PATH) not in sys.path:
    sys.path.insert(0, str(COMMON_PATH))

from aegis_common.rule_test_runner import evaluate_profile_against_samples

def main() -> None:
    parser = argparse.ArgumentParser(description="Test recommendation rule profiles against sample telemetry metric windows.")
    parser.add_argument("--profile", default="default_recommendation_rules", help="Recommendation rule profile name")
    parser.add_argument("--rule-dir", default=str(ROOT / "recommendation_rules"), help="Directory containing recommendation rule profiles")
    parser.add_argument("--sample-dir", default=str(ROOT / "recommendation_rules" / "tests"), help="Directory containing rule test samples")
    parser.add_argument("--output-json", default="", help="Optional path to write JSON test report")
    parser.add_argument("--fail-on-error", action="store_true", help="Exit non-zero if any sample fails")
    args = parser.parse_args()

    report = evaluate_profile_against_samples(
        profile_name=args.profile,
        rule_dir=args.rule_dir,
        sample_dir=args.sample_dir,
    )

    print(json.dumps(report, indent=2))

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.fail_on_error and report["failed"] > 0:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
