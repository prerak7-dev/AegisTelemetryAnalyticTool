from aegis_common.rule_based_recommendation_engine import evaluate_condition, evaluate_rules

def test_nested_condition_matches():
    metrics = {"p95_frame": 70, "packet_loss_p95": 5, "active_players": 150}
    condition = {
        "all": [
            {"metric": "active_players", "op": ">=", "value": 120},
            {"any": [
                {"metric": "p95_frame", "op": ">=", "value": 50},
                {"metric": "packet_loss_p95", "op": ">=", "value": 10}
            ]}
        ]
    }
    assert evaluate_condition(condition, metrics)

def test_custom_rule_evaluates():
    profile = {
        "rules": [
            {
                "id": "custom_test_rule",
                "enabled": True,
                "title": "Custom Test Rule",
                "owner": "Test Team",
                "impact": "Test impact",
                "condition": {"metric": "p95_frame", "op": ">=", "value": 50},
                "score": {
                    "weighted_sum": [
                        {"metric": "p95_frame", "min": 35, "max": 90, "weight": 1.0}
                    ],
                    "minimum": 0.1
                },
                "confidence": {
                    "base": 0.5,
                    "weighted_sum": [
                        {"metric": "p95_frame", "min": 35, "max": 90, "weight": 0.2}
                    ],
                    "max": 0.9
                },
                "evidence_fields": ["p95_frame"],
                "recommended_actions": ["Do a specific thing."],
                "investigation_steps": ["Investigate a specific thing."],
                "validation_plan": ["Validate a specific thing."],
                "guardrail_metrics": ["guardrail_metric"],
                "tradeoffs": ["tradeoff"]
            }
        ]
    }

    metrics = {"p95_frame": 75}
    issues = evaluate_rules(metrics, profile)
    assert issues[0]["issue_type"] == "custom_test_rule"
    assert issues[0]["recommended_actions"] == ["Do a specific thing."]
