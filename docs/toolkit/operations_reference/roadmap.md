# Roadmap

Completed phases include:

| Phase | Capability |
|---|---|
| Phase 1-6 | Telemetry ingestion, dashboarding, incidents, configurable rules, incident replay |
| Phase 7 | Baselines, anomaly detection, query hardening |
| Phase 8 | Build regression analysis |
| Phase 9 | Experimentation and fix validation |
| Phase 10 | Incident workflow and ownership |
| Phase 11 | Portfolio demo mode and scenario library |
| Phase 12 | Analyst exports, notebooks, SQL templates |
| Phase 12.5 | Professional documentation workspace |
| Phase 13 | Production readiness layer |

## Current production-readiness layer

Phase 13 now adds:

- OpenAPI contract
- API contract tests
- collector metrics endpoint
- Prometheus scrape config
- Grafana dashboard seed
- OpenTelemetry collector starter config
- Kafka retention and DLQ documentation
- load testing profile
- ClickHouse partitioning and TTL documentation
- deployment and readiness checklists

## Next recommended phase

```text
Production hardening implementation pass
```

Recommended future implementation additions:

- CI pipeline for contract tests
- automated OpenAPI generation and diff checks
- full Prometheus/Grafana provisioning
- OpenTelemetry instrumentation in collector and processor
- Kafka consumer lag dashboard
- true database-backed incident workflow store
- ClickHouse materialized views for rollups
- Kubernetes/ECS deployment manifests
- secrets management and environment profiles

## Long-term direction

The toolkit should become credible to:

- live-ops analysts
- data analysts
- backend engineers
- game systems engineers
- data platform teams
- technical reviewers
