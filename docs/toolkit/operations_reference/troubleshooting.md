# Troubleshooting

## Dashboard says no scenarios are configured

Check that the dashboard container has access to:

```text
/app/config/demo_scenarios.json
```

In Docker Compose, confirm:

```text
./config:/app/config:ro
```

## Data takes a few seconds to appear after starting a demo

This is expected.

Pipeline stages:

```text
simulator
collector
Kafka/Redpanda
processor raw insert
aggregate window close
incident generation
dashboard query refresh
```

Use the Demo Control Center Live Demo Feedback panel to see raw events before aggregates are ready.

## ClickHouse authentication failed

If ClickHouse password/config changed, old Docker volumes may retain the previous user configuration.

Fix:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

## Source profile column missing

If you added schema fields after a previous ClickHouse volume was created, the old table may not have new columns.

For local development:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

## Streamlit widget state warning

Avoid setting a widget key in `st.session_state` after the widget has been created. Use canonical state and callbacks for robust persistence.

## Filters reset on refresh

The sidebar uses canonical persisted state plus query parameters. If filters reset, check for:

- widget key mismatch
- options list no longer containing the selected value
- code overwriting session state after render
