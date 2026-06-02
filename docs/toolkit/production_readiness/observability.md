# Observability

Production analytics systems need clear operational signals.

## Metrics

The collector exposes Prometheus-compatible metrics at:

```text
GET /metrics
```

Current metrics include:

```text
aegis_collector_accepted_events_total
aegis_collector_failed_events_total
aegis_collector_mapped_events_total
aegis_collector_sampled_or_dropped_events_total
aegis_collector_adaptive_sampling_enabled
aegis_collector_load_shed_batch_threshold
```

## Health

The collector exposes:

```text
GET /health
```

Use this for readiness/liveness checks.

## Prometheus

Config:

```text
infra/observability/prometheus.yml
```

Optional compose overlay:

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build
```

Prometheus URL:

```text
http://localhost:9090
```

## Grafana

Dashboard seed:

```text
infra/observability/grafana/aegis_telemetry_dashboard.json
```

Grafana URL:

```text
http://localhost:3000
```

Default local credentials:

```text
admin / aegis
```

## Structured logging strategy

Recommended log fields:

```text
timestamp
level
service
event
request_id
trace_id
source_profile
region
server_id
topic
partition
offset
duration_ms
rows_written
error_type
```

## Trace strategy

Use OpenTelemetry for cross-service traces:

```text
collector ingest request
  ↓
Kafka publish
  ↓
processor consume
  ↓
ClickHouse insert
  ↓
dashboard query
```

A starter OpenTelemetry collector config is included at:

```text
infra/observability/otel-collector-config.yaml
```

## Alert examples

| Signal | Alert |
|---|---|
| Collector failed events | Validation failure rate above threshold |
| Dropped events | Adaptive load shedding active too long |
| Kafka consumer lag | Processor falling behind |
| ClickHouse insert failures | Data pipeline degradation |
| Dashboard query budgets | User-facing analytics slow |
