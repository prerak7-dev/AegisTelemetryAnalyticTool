# Telemetry Flow

## Event generation

The simulator generates telemetry with fields such as:

- scenario
- source profile
- server
- region
- map
- zone
- build version
- frame time
- packet out
- packet loss
- replication count
- physics events
- memory
- player impact symptoms

## Collector

The collector accepts batches at:

```text
POST /v1/events
```

It publishes events to Redpanda/Kafka.

## Processor

The processor:

1. consumes events
2. inserts raw events
3. aggregates 30-second windows
4. evaluates recommendation rules
5. writes incidents

## Dashboard

The dashboard reads:

```text
raw_events
agg_zone_30s
data_quality_failures
incidents
```

and optional local stores:

```text
data/incident_workflow.json
data/demo_scenario_history.json
```

## Why aggregates may lag raw events

The dashboard can see raw events before aggregate windows are complete.

Aggregate visibility depends on:

```text
window length
processor flush cadence
window grace seconds
ClickHouse insert timing
dashboard refresh timing
```

This is why the Demo Control Center shows separate raw and aggregate feedback.
