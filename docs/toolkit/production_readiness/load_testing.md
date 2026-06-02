# Load Testing

A collector load-test profile is included at:

```text
tools/load_test_collector.py
```

## Basic test

```bash
python tools/load_test_collector.py \
  --collector-url http://localhost:8000 \
  --events-per-second 500 \
  --duration-sec 300 \
  --batch-size 250 \
  --workers 8
```

## What it reports

```text
submitted batches
submitted events
HTTP status counts
average latency
p95 latency
p99 latency
failure samples
```

## Suggested local profiles

### Smoke

```bash
python tools/load_test_collector.py --events-per-second 100 --duration-sec 60
```

### Portfolio demo

```bash
python tools/load_test_collector.py --events-per-second 500 --duration-sec 180
```

### Stress

```bash
python tools/load_test_collector.py --events-per-second 1500 --duration-sec 300 --workers 16
```

## What to watch during load tests

- collector `/metrics`
- collector `/health`
- Redpanda broker health
- processor lag
- ClickHouse insert throughput
- dashboard query budgets
- adaptive load shedding counters
- validation failure rate

## Performance acceptance examples

For a local portfolio environment:

```text
Collector p95 batch latency < 250 ms
HTTP 2xx rate > 99%
Processor lag recovers after load burst
Dashboard query budgets remain acceptable
No uncontrolled memory growth
```

For production, replace these with environment-specific SLOs.
