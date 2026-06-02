# Toolkit Overview

AegisTelemetry is a live-operations analytics toolkit for high-traffic multiplayer game telemetry. It is designed to demonstrate how game teams can move from raw event streams to operational decisions.

The toolkit supports:

- realtime command-center monitoring
- source-schema adaptable telemetry
- data-quality review
- configurable incident rules and recommendations
- historical incident replay and root-cause timelines
- baseline-aware anomaly detection
- build regression analysis
- fix validation through control/treatment experiments
- incident ownership and workflow
- portfolio demo scenarios
- analyst exports, SQL templates, and notebooks

## Intended audience

AegisTelemetry is built for three groups:

| Audience | What they use |
|---|---|
| Live-ops analysts | Command Center, Incident Dossier, Incident Timeline, Incident Workflow |
| Data analysts | Baseline Intelligence, Build Regression, Fix Validation, Analyst Toolkit |
| Developers/platform engineers | Configuration, source schemas, rules, query performance, simulator, Docker services |

## Core idea

The toolkit is not just a chart dashboard. The intended flow is:

```text
Ingest telemetry
  ↓
Validate source schema
  ↓
Aggregate by gameplay context
  ↓
Detect pressure / anomalies / incidents
  ↓
Explain likely driver
  ↓
Recommend action
  ↓
Assign owner
  ↓
Validate fix
  ↓
Export evidence
```

## Architecture at a glance

```text
Simulator
  ↓ HTTP
Collector
  ↓ Redpanda/Kafka
Processor
  ↓ ClickHouse
Dashboard
  ↓
Operational workspaces + analyst notebooks
```

## Configuration-first design

Most thresholds, table names, workspaces, scenario settings, baseline settings, and documentation navigation are configuration-backed. The goal is to make the toolkit adaptable to different games and telemetry conventions without rewriting view logic.
