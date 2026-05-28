# Phase 5.2 — Incident Dossier Rule ID Filter

This patch adds rule ID / likely-driver filtering to the Incident Dossier.

## What changed

The Incident Dossier now supports filtering by:

```text
Incident severity
Rule ID / likely driver
```

Rule ID options are loaded from both:

- configured recommendation rule profile JSON files under `recommendation_rules/`
- observed incident `likely_driver` values in ClickHouse

This means analysts can filter by built-in and custom rule IDs, including:

```text
memory_pressure
unclassified_performance_pressure
physics_simulation_spike
network_packet_pressure
ai_pathfinding_pressure
aoe_replication_overload
local_density_tick_budget
matchmaking_or_capacity_surge
desync_hit_registration_risk
```

## Dashboard behavior

The Incident Dossier now shows a severity/rule distribution table before incident cards, making it easier to triage by category.
