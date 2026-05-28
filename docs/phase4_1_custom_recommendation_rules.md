# Phase 4.1 — Custom Recommendation Rules

Phase 4.1 makes issue detection and solution guidance data-driven.

Developers can now add/edit rules under:

```text
recommendation_rules/
  default_recommendation_rules.json
  custom_rules_example.json
```

The processor loads the active rule profile from:

```text
RECOMMENDATION_RULE_PROFILE=default_recommendation_rules
RECOMMENDATION_RULE_DIR=/app/recommendation_rules
```

## Supported condition operators

```text
>  >=  <  <=  ==  !=  contains  not_contains  in  not_in
```

## Rule structure

Each rule can define:

- `condition`
- `score`
- `confidence`
- `evidence_fields`
- `recommended_actions`
- `investigation_steps`
- `validation_plan`
- `guardrail_metrics`
- `tradeoffs`

## Adding a custom rule profile

1. Copy:

```text
recommendation_rules/custom_rules_example.json
```

2. Rename it:

```text
recommendation_rules/my_studio_rules.json
```

3. Change:

```json
"profile_name": "my_studio_rules"
```

4. Add/edit rules.

5. Set:

```yaml
RECOMMENDATION_RULE_PROFILE: my_studio_rules
```

6. Rebuild:

```bash
docker compose down
docker compose up --build
```

The dashboard includes a `Recommendation Rules` workspace that shows available rule profiles and an example rule template.


## Out-of-the-box default rules

`default_recommendation_rules.json` includes the full built-in issue set:

- `aoe_replication_overload`
- `physics_simulation_spike`
- `network_packet_pressure`
- `local_density_tick_budget`
- `ai_pathfinding_pressure`
- `memory_pressure`
- `matchmaking_or_capacity_surge`
- `desync_hit_registration_risk`

Developers can disable any rule with:

```json
"enabled": false
```

or copy the default profile into a studio-specific profile and tune thresholds/actions there.
