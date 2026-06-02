# Production Readiness Overview

Phase 13 adds the production-readiness layer for AegisTelemetry.

The goal is to make the project credible not only as a dashboard, but as a service-oriented analytics system that can be reviewed by backend, data-platform, online-services, and live-operations teams.

## What production readiness means here

Production readiness covers:

- API contracts
- contract tests
- health checks
- metrics
- structured logs
- tracing strategy
- Kafka topic retention
- dead-letter handling
- ClickHouse partitioning
- load testing
- deployment checklist
- operational runbooks

## New production assets

| Asset | Location |
|---|---|
| Collector OpenAPI contract | `openapi/collector.openapi.json` |
| Contract tests | `tests/contract/` |
| Prometheus config | `infra/observability/prometheus.yml` |
| Grafana dashboard seed | `infra/observability/grafana/aegis_telemetry_dashboard.json` |
| Optional observability compose | `docker-compose.observability.yml` |
| Load test profile | `tools/load_test_collector.py` |
| Production docs | `docs/toolkit/production_readiness/` |

## Service maturity path

```text
Local MVP
  ↓
API contracts
  ↓
Contract tests
  ↓
Metrics + logs + traces
  ↓
Load testing
  ↓
Retention + DLQ
  ↓
Deployment docs
  ↓
Operational readiness checklist
```

## Readiness principle

Do not call the system production-ready just because it runs locally. It should be explainable, observable, testable, and recoverable.
