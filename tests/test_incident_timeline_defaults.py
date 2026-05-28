import json
from pathlib import Path

def test_default_profile_exists_and_example_is_not_only_profile():
    profiles = sorted(path.stem for path in Path("timeline_stages").glob("*.json"))
    assert "default_timeline_stages" in profiles
    assert "custom_timeline_stages_example" in profiles

def test_default_profile_has_longer_rule_specific_sequences():
    payload = json.loads(Path("timeline_stages/default_timeline_stages.json").read_text(encoding="utf-8"))
    for rule_id, sequence in payload["rule_sequences"].items():
        assert len(sequence) >= 5, f"{rule_id} should not use the short example sequence"

def test_custom_example_is_marked_example_only():
    payload = json.loads(Path("timeline_stages/custom_timeline_stages_example.json").read_text(encoding="utf-8"))
    assert "Example-only" in payload["description"]
