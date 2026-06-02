# Phase 13 — Production Readiness Layer

This phase adds the production-readiness layer for AegisTelemetry.

## Added

```text
OpenAPI contract
contract tests
Prometheus metrics endpoint
Prometheus scrape config
Grafana dashboard seed
OpenTelemetry collector starter config
Kafka retention and DLQ docs
ClickHouse partitioning and TTL docs
collector load-test profile
deployment checklist
readiness checklist
documentation workspace updates
```

## Runtime change

Collector now exposes:

```text
GET /metrics
```

with Prometheus-compatible counters.

## New files

```text
openapi/collector.openapi.json
tests/contract/test_collector_openapi_contract.py
tests/contract/test_production_docs_inventory.py
infra/observability/prometheus.yml
infra/observability/grafana/aegis_telemetry_dashboard.json
infra/observability/otel-collector-config.yaml
docker-compose.observability.yml
tools/load_test_collector.py
docs/toolkit/production_readiness/
```

## Documentation workspace

The documentation registry now includes:

```text
Production Readiness
```

with pages for:

```text
overview
OpenAPI contracts
observability
Kafka retention and DLQ
ClickHouse partitioning
load testing
deployment checklist
readiness checklist
```

## Run contract tests

```bash
pytest tests/contract
```

## Run optional observability stack

```bash
docker compose -f docker-compose.yml -f docker-compose.observability.yml up --build
```

Prometheus:

```text
http://localhost:9090
```

Grafana:

```text
http://localhost:3000
```

## Run load test

```bash
python tools/load_test_collector.py \
  --collector-url http://localhost:8000 \
  --events-per-second 500 \
  --duration-sec 300
```
