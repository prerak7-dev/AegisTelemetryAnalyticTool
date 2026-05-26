# AegisTelemetry — Real-Time Gameplay Performance Intelligence

A production-style portfolio project for analyzing high-volume gameplay telemetry, detecting realtime server-performance incidents, and generating evidence-backed optimization recommendations for AAA live-service games.

## Core agenda

This tool answers:

1. Where is server performance degrading right now?
2. Which gameplay behaviors are correlated with the degradation?
3. Is the issue caused by crowding, combat events, physics, object replication, network pressure, or scaling pressure?
4. What optimization should engineers/designers test next?

The MVP includes:

- Synthetic gameplay/server/network telemetry generator.
- FastAPI regional telemetry collector.
- Redpanda Kafka-compatible realtime event stream.
- Python stream processor with rolling-window aggregation.
- ClickHouse realtime analytical storage.
- Incident detector for hot zones, server hitches, network degradation, and scaling risk.
- Streamlit dashboard shell.
- Event schemas, data quality rules, and production scaling notes.

## Local architecture

```text
Synthetic game/server simulator
        ↓
FastAPI telemetry collector
        ↓
Redpanda topics
        ↓
Realtime processor
        ↓
ClickHouse raw + aggregate tables
        ↓
Streamlit dashboard
```

## Quick start

Requirements:

- Docker Desktop
- Python 3.11+ only if running simulator outside Docker

Start the stack:

```bash
docker compose up --build
```

Open:

```text
Collector health: http://localhost:8000/health
Streamlit dashboard: http://localhost:8501
Redpanda Console: http://localhost:8080
ClickHouse HTTP: http://localhost:8123
```

Generate traffic from your host machine:

```bash
cd simulator
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 180
```

Linux/macOS activation:

```bash
source .venv/bin/activate
```

## Scenarios

- `normal_load`
- `weekend_event_meltdown`
- `physics_spike`
- `region_login_surge`
- `replication_overload`

Most important demo:

```bash
python generate_traffic.py --scenario weekend_event_meltdown --events-per-second 1000 --duration-sec 300
```

## Production scaling story

The local version is intentionally small enough to run on a laptop. The architecture is designed around high-traffic live-service constraints:

- Regional collectors
- Kafka-compatible partitioned event streams
- Priority-aware telemetry
- Hot/warm/cold data paths
- Rolling-window stream aggregation
- ClickHouse realtime OLAP
- Incident recommendations with evidence and confidence
- Backpressure and adaptive sampling design
- Production upgrade path to Kubernetes, Flink/Kafka Streams, ClickHouse clusters, object storage, and Prometheus/Grafana SLOs


## ClickHouse auth reset

If you see `AUTHENTICATION_FAILED` from the processor or dashboard, reset the local ClickHouse volume because credentials are persisted after the first initialization:

```bash
docker compose down -v
docker compose up --build
```

This MVP uses the local development password:

```text
CLICKHOUSE_PASSWORD=aegis_dev_password
```

Do not use this password in production.


## Phase 2 features

This version adds:

- Incident attribution scoring with ranked likely drivers.
- Data-quality failure stream and dashboard tab.
- Adaptive collector sampling under high-volume batches.
- More stable high-traffic scenario topology.
- Dashboard tabs for command center, incident deep dive, data quality, and scaling readiness.

Because this version adds a new ClickHouse table, reset local volumes when upgrading:

```bash
docker compose down -v
docker compose up --build
```

Optional data-quality demo:

```bash
cd simulator
python generate_traffic.py --scenario weekend_event_meltdown --collector-url http://localhost:8000 --events-per-second 500 --duration-sec 120 --invalid-rate 0.02
```
