from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aegis_common.rule_based_recommendation_engine import evaluate_rules, get_active_profile, load_rule_profiles

@dataclass(frozen=True)
class RuleTestResult:
    sample_id: str
    description: str
    expected_issue_ids: list[str]
    actual_issue_ids: list[str]
    top_issue_id: str | None
    passed: bool
    matched_expected: list[str]
    missing_expected: list[str]
    unexpected_top_issue: str | None
    issue_candidates: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "sample_id": self.sample_id,
            "description": self.description,
            "expected_issue_ids": self.expected_issue_ids,
            "actual_issue_ids": self.actual_issue_ids,
            "top_issue_id": self.top_issue_id,
            "passed": self.passed,
            "matched_expected": self.matched_expected,
            "missing_expected": self.missing_expected,
            "unexpected_top_issue": self.unexpected_top_issue,
            "issue_candidates": self.issue_candidates,
        }

def load_sample(path: str | Path) -> dict[str, Any]:
    sample_path = Path(path)
    payload = json.loads(sample_path.read_text(encoding="utf-8"))

    if "metrics" not in payload:
        raise ValueError(f"Rule test sample '{sample_path}' is missing a 'metrics' object")

    payload.setdefault("sample_id", sample_path.stem)
    payload.setdefault("description", "")
    payload.setdefault("expected_issue_ids", [])
    return payload

def load_samples(sample_dir: str | Path) -> list[dict[str, Any]]:
    sample_path = Path(sample_dir)
    if not sample_path.exists():
        return []

    return [load_sample(path) for path in sorted(sample_path.glob("*.json"))]

def evaluate_sample(sample: dict[str, Any], profile: dict[str, Any]) -> RuleTestResult:
    issue_candidates = evaluate_rules(sample["metrics"], profile)
    actual_issue_ids = [candidate.get("issue_type", "") for candidate in issue_candidates]
    expected_issue_ids = list(sample.get("expected_issue_ids", []))
    top_issue_id = actual_issue_ids[0] if actual_issue_ids else None

    matched_expected = [issue_id for issue_id in expected_issue_ids if issue_id in actual_issue_ids]
    missing_expected = [issue_id for issue_id in expected_issue_ids if issue_id not in actual_issue_ids]

    # A sample passes when every expected issue appears somewhere in the ranked
    # candidates and the top result is one of the expected issues.
    unexpected_top_issue = None
    passed = not missing_expected
    if expected_issue_ids:
        if top_issue_id not in expected_issue_ids:
            unexpected_top_issue = top_issue_id
            passed = False
    else:
        passed = len(actual_issue_ids) == 0

    return RuleTestResult(
        sample_id=sample["sample_id"],
        description=sample.get("description", ""),
        expected_issue_ids=expected_issue_ids,
        actual_issue_ids=actual_issue_ids,
        top_issue_id=top_issue_id,
        passed=passed,
        matched_expected=matched_expected,
        missing_expected=missing_expected,
        unexpected_top_issue=unexpected_top_issue,
        issue_candidates=issue_candidates,
    )

def evaluate_profile_against_samples(
    profile_name: str = "default_recommendation_rules",
    rule_dir: str | Path = "recommendation_rules",
    sample_dir: str | Path = "recommendation_rules/tests",
) -> dict[str, Any]:
    profiles = load_rule_profiles(rule_dir)
    profile = profiles.get(profile_name) or get_active_profile(rule_dir=rule_dir, profile_name=profile_name)
    samples = load_samples(sample_dir)

    results = [evaluate_sample(sample, profile) for sample in samples]
    passed = sum(1 for result in results if result.passed)
    failed = len(results) - passed

    return {
        "profile_name": profile.get("profile_name", profile_name),
        "profile_version": profile.get("version", "unknown"),
        "sample_count": len(samples),
        "passed": passed,
        "failed": failed,
        "pass_rate": round(passed / len(samples), 3) if samples else 0.0,
        "results": [result.to_dict() for result in results],
    }

def evaluate_single_metrics(
    metrics: dict[str, Any],
    profile_name: str = "default_recommendation_rules",
    rule_dir: str | Path = "recommendation_rules",
) -> dict[str, Any]:
    profiles = load_rule_profiles(rule_dir)
    profile = profiles.get(profile_name) or get_active_profile(rule_dir=rule_dir, profile_name=profile_name)
    issues = evaluate_rules(metrics, profile)
    return {
        "profile_name": profile.get("profile_name", profile_name),
        "issue_candidates": issues,
    }
