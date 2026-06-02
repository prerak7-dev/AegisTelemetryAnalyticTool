# Deployment Checklist

## Before deployment

- Confirm OpenAPI contract is current.
- Run contract tests.
- Run load-test smoke profile.
- Confirm ClickHouse tables initialize successfully.
- Confirm Redpanda topics exist.
- Confirm source schemas are loaded.
- Confirm recommendation rules are loaded.
- Confirm timeline stages are loaded.
- Confirm dashboard config path is correct.

## Runtime checks

Collector:

```text
GET /health
GET /metrics
```

Dashboard:

```text
http://localhost:8501
```

Redpanda Console:

```text
http://localhost:8080
```

ClickHouse:

```text
http://localhost:8123/ping
```

## Observability checks

- Prometheus can scrape collector.
- Grafana can load dashboard.
- Failed events counter is visible.
- Dropped events counter is visible.
- Query Performance workspace shows query budgets.

## Data checks

- raw events are inserted.
- aggregate windows appear.
- incidents appear when scenario pressure is high.
- data-quality failures appear when invalid-rate is used.
- demo scenarios update Live Demo Feedback.

## Rollback

For local demo:

```bash
docker compose down --remove-orphans
docker compose up --build
```

For full reset:

```bash
docker compose down -v --remove-orphans
docker compose up --build
```

## Promotion gate

Do not promote if:

- contract tests fail
- health endpoints fail
- collector cannot publish
- processor cannot consume
- ClickHouse cannot write
- dashboard cannot query
- validation failure rate is unexplained
- consumer lag does not recover
