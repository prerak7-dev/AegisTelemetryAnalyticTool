# Phase 5 — Rule Testing and Replay

Phase 5 makes recommendation rules testable before they are trusted in live incident analysis.

## What this adds

```text
recommendation_rules/tests/
  aoe_replication_overload_sample.json
  physics_simulation_spike_sample.json
  network_packet_pressure_sample.json
  local_density_tick_budget_sample.json
  ai_pathfinding_pressure_sample.json
  memory_pressure_sample.json
  matchmaking_capacity_surge_sample.json
  desync_hit_registration_sample.json
```

Each sample contains:

- `sample_id`
- `description`
- `expected_issue_ids`
- `metrics`

## CLI test runner

Run all rule tests:

```bash
python tools/test_recommendation_rules.py --profile default_recommendation_rules
```

Fail the command if any sample fails:

```bash
python tools/test_recommendation_rules.py --profile default_recommendation_rules --fail-on-error
```

Write a JSON report:

```bash
python tools/test_recommendation_rules.py --output-json reports/rule_test_report.json
```

Preview one sample:

```bash
python tools/preview_recommendation.py recommendation_rules/tests/ai_pathfinding_pressure_sample.json
```

## Dashboard workspace

The dashboard now includes:

```text
Rule Testing
```

It shows:

- selected rule profile
- pass/fail summary
- expected vs actual issue IDs
- ranked issue candidates for a selected sample
- top issue evidence/actions/validation plan
- raw sample metrics

## Why this matters

Custom recommendation rules should be governed like code. Developers can now test rules against known telemetry patterns before enabling them in live analysis.
