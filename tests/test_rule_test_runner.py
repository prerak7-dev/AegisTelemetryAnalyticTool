from aegis_common.rule_test_runner import evaluate_profile_against_samples

def test_default_rule_samples_pass():
    report = evaluate_profile_against_samples(
        profile_name="default_recommendation_rules",
        rule_dir="recommendation_rules",
        sample_dir="recommendation_rules/tests",
    )
    assert report["sample_count"] >= 8
    assert report["failed"] == 0
