# System Architecture

## Services

```text
simulator/
  Generates gameplay telemetry

collector/
  FastAPI HTTP ingestion service
  Validates request shape
  Publishes to Redpanda/Kafka

processor/
  Consumes Kafka events
  Writes raw events
  Aggregates windows
  Applies recommendation rules
  Emits incidents

dashboard/
  Streamlit UI
  Queries ClickHouse
  Renders workspaces
  Hosts configuration, docs, exports, and demo controls

clickhouse/
  Analytics store

redpanda/
  Kafka-compatible stream
```

## Data flow

```text
generate_traffic.py
  ↓ HTTP /v1/events
collector
  ↓ Kafka topic
processor
  ↓ ClickHouse
raw_events
  ↓ window aggregation
agg_zone_30s
  ↓ rules
incidents
  ↓ dashboard
workspaces
```

## Design principles

- configuration over hardcoding
- graceful degradation when optional data is missing
- dashboard-side views backed by reusable helpers
- evidence-first incident handling
- explicit source-profile support
- query budgets and diagnostics
- local demo mode without external infrastructure

## Extension points

| Extension | Where |
|---|---|
| New workspace | `services/dashboard/views/` + `workspaces.py` |
| New source schema | `source_schemas/` |
| New incident rule | `recommendation_rules/` |
| New timeline stage | `timeline_stages/` |
| New demo scenario | `config/demo_scenarios.json` |
| New documentation page | `docs/toolkit/` + `config/documentation_navigation.json` |
| New SQL template | `sql/analyst_templates/` |
| New notebook | `notebooks/` |
