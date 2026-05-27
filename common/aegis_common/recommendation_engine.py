from __future__ import annotations

from typing import Any

from aegis_common.rule_based_recommendation_engine import evaluate_rules, top_rule_issue

def evaluate_issues(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    """Evaluate incidents through data-driven recommendation rules.

    Rule files live under `recommendation_rules/`. Developers can add/edit
    rules without touching this Python module.
    """
    return evaluate_rules(metrics)

def top_issue(metrics: dict[str, Any]) -> dict[str, Any]:
    return top_rule_issue(metrics)
