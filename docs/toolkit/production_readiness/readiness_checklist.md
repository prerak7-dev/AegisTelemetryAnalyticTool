# Production Readiness Checklist

## API and contracts

- [ ] OpenAPI contract is present.
- [ ] Contract tests pass.
- [ ] API changes are backward compatible.
- [ ] Example requests are documented.
- [ ] Error responses are documented.

## Observability

- [ ] `/health` works.
- [ ] `/metrics` works.
- [ ] Prometheus scrape config is present.
- [ ] Grafana dashboard seed is present.
- [ ] Structured logging fields are documented.
- [ ] Trace strategy is documented.

## Kafka / Redpanda

- [ ] Topic names are documented.
- [ ] Retention policy is documented.
- [ ] DLQ topic is documented.
- [ ] Poison-message path is documented.
- [ ] Consumer lag monitoring is planned.

## ClickHouse

- [ ] Core table order keys are documented.
- [ ] Partition strategy is documented.
- [ ] TTL strategy is documented.
- [ ] Rollup candidates are documented.
- [ ] Dashboard queries use bounded filters.

## Testing

- [ ] Contract tests exist.
- [ ] Load-test profile exists.
- [ ] Load-test acceptance notes exist.
- [ ] Failure-mode testing is planned.

## Operations

- [ ] Deployment checklist is present.
- [ ] Troubleshooting guide is present.
- [ ] Reset/rollback procedure is documented.
- [ ] Incident workflow exists.
- [ ] Exportable incident reports exist.

## Portfolio readiness

- [ ] Demo Control Center works.
- [ ] Documentation workspace includes production readiness.
- [ ] Analyst Toolkit exports evidence.
- [ ] Build Regression and Fix Validation work with generated scenarios.
